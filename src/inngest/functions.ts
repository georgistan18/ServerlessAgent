import { inngest } from "./client";
import { put, del } from "@vercel/blob";
// Removed uuid as slug should be unique enough with date and topics

const NEWSLETTER_READ_WRITE_TOKEN = process.env.NEWSLETTER_READ_WRITE_TOKEN;
if (!NEWSLETTER_READ_WRITE_TOKEN) {
  throw new Error('NEWSLETTER_READ_WRITE_TOKEN env variable is required');
}

// Define data structure for the initial event
interface NewsletterGenerateRequestedData {
  slug: string;
  blobKey: string;
  topics: string[];
}

interface PythonAgentResponse {
  content: string;
  riskSummary: string;
}


// Main Inngest function with multi-step workflow
export const generateNewsletter = inngest.createFunction(
  { id: "generate-newsletter" },
  { event: "newsletter/generate.requested" },
  async ({ event, step }: { event: { data: NewsletterGenerateRequestedData }; step: unknown }) => {
    console.log("Generating newsletter for slug:", event.data.slug);
    const { topics, slug, blobKey } = event.data;
    if (!topics || !slug || !blobKey) {
      throw new Error("Missing topics, slug, or blobKey in event data.");
    }

    function assertStepHasRun(s: unknown): asserts s is { run: (name: string, fn: () => Promise<unknown>) => Promise<unknown> } {
      if (!s || typeof s !== 'object' || typeof (s as { run?: unknown }).run !== 'function') {
        throw new Error('step.run is not available');
      }
    }
    assertStepHasRun(step);

    // Step 0:Write placeholder blob first
    // This is to solve the stuck frontend page stuck on generating issue
    await writeInitialPlaceholderBlob(blobKey, slug);

    // Step 1: Call Python Agent
    const rawAgentContentUnknown = await step.run("call-python-agent", () => callPythonAgent(topics, slug));
    if (!rawAgentContentUnknown || typeof rawAgentContentUnknown !== 'object' || !('content' in rawAgentContentUnknown)) {
      throw new Error('Python agent did not return expected content');
    }
    const { content: rawAgentContent, riskSummary } = rawAgentContentUnknown as PythonAgentResponse;

    // Step 2: Format Newsletter with Markdown Agent
    const formattedContentUnknown = await step.run("format-newsletter", () => formatNewsletter(rawAgentContent, topics, slug));
    if (typeof formattedContentUnknown !== 'string') {
      throw new Error('Formatting agent did not return a string');
    }
    const formattedContent = formattedContentUnknown;

    // Combine the formatted content with the risk summary
    const finalContent = `${formattedContent}\n\n## Risk Analysis\n\n${riskSummary}`;

    // add diagnostics logs to verify that the final content is being saved
    console.log("[Inngest] Final content to save:", finalContent.slice(0, 200));
    console.log("[Inngest] Using blobKey:", blobKey);

    // Step 3: Save Newsletter to Blob
    const finalBlobUnknown = await step.run("save-to-blob", () => saveNewsletterToBlob(blobKey, finalContent, slug));
    if (!finalBlobUnknown || typeof finalBlobUnknown !== 'object' || typeof (finalBlobUnknown as { url?: unknown }).url !== 'string') {
      throw new Error('Blob result missing url');
    }
    const finalBlob = finalBlobUnknown as { url: string };

    return { url: finalBlob.url, message: `Newsletter generated and saved for ${slug}` };
  }
);

// --- Step implementations below ---

// Helper function to get the Python agent URL
function getPythonAgentUrl(): string {
  // Use custom APP_URL if set (recommended approach)
  if (process.env.APP_URL) {
    return `${process.env.APP_URL}/api/agents`;
  }
  
  // For local development
  if (!process.env.VERCEL) {
    return 'http://localhost:8000';
  }
  
  // For production, use the production URL
  if (process.env.VERCEL_ENV === 'production' && process.env.VERCEL_PROJECT_PRODUCTION_URL) {
    return `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}/api/agents`;
  }
  
  // For preview deployments, use branch URL
  if (process.env.VERCEL_BRANCH_URL) {
    return `https://${process.env.VERCEL_BRANCH_URL}/api/agents`;
  }
  
  // Fallback
  console.warn('[Inngest] No suitable URL found for Python agent, using deployment URL');
  return `https://${process.env.VERCEL_URL}/api/agents`;
}

async function callPythonAgent(topics: string[], slug: string): Promise<PythonAgentResponse> {
  const pythonAgentUrl = getPythonAgentUrl();
  
  try {
    const response = await fetch(`${pythonAgentUrl}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topics }),
    });

    if (!response.ok) {
      console.error(`[Inngest] Research agent request failed for slug ${slug}. Status: ${response.status}`);
      throw new Error(`Research agent request failed with status ${response.status}`);
    }

    const data = await response.json();
    const content = data.content;
    const riskSummary = data.risk_summary;
    
    if (!content) {
      throw new Error('Research agent returned no content');
    }

    // Log the structured data from the response
    // frontend (via Inngest) sends a request to the FastAPI /api/agents/research endpoint.
    // hat endpoint returns both content and structured_data
    // Added this line to confirm that structured_data exists, is well-formed, and reaches this part of your workflow.
    // structure_data should be seen now in the node.js terminal or in the Vercel deployment logs if run in production 
    console.log('Structured data from research agent:', data.structured_data);
    console.log('Risk summary from research agent:', riskSummary);

    return { content, riskSummary };
  } catch (error) {
    console.error(`[Inngest] Research agent error for slug ${slug}:`, error);
    throw error;
  }
}

async function formatNewsletter(rawContent: string, topics: string[], slug: string) {
  // Build the appropriate URL based on environment
  let pythonAgentUrl: string;
  if (!process.env.VERCEL) {
    // Local development
    pythonAgentUrl = 'http://localhost:8000';
  } else if (process.env.VERCEL_ENV === 'production' && process.env.VERCEL_PROJECT_PRODUCTION_URL) {
    // Production environment - use the production URL
    pythonAgentUrl = `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}/api/agents`;
  } else if (process.env.VERCEL_BRANCH_URL) {
    // Preview environment - use the branch URL which is more stable than VERCEL_URL
    pythonAgentUrl = `https://${process.env.VERCEL_BRANCH_URL}/api/agents`;
  } else {
    // Fallback to deployment URL if nothing else is available
    pythonAgentUrl = `https://${process.env.VERCEL_URL}/api/agents`;
  }
  
  try {
    const response = await fetch(`${pythonAgentUrl}/format`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        raw_content: rawContent,
        topics: topics 
      }),
    });

    if (!response.ok) {
      console.error(`[Inngest] Formatting agent request failed for slug ${slug}. Status: ${response.status}`);
      throw new Error(`Formatting agent request failed with status ${response.status}`);
    }

    const data = await response.json();
    const content = data.content;
    
    if (!content) {
      throw new Error('Formatting agent returned no content');
    }

    return content;
  } catch (error) {
    console.error(`[Inngest] Formatting agent error for slug ${slug}:`, error);
    throw error;
  }
}

async function saveNewsletterToBlob(blobKey: string, rawAgentContent: string, slug: string) {
  if (typeof rawAgentContent !== "string") {
    console.error(`[Inngest] Invalid content type for slug ${slug}. Expected string, got ${typeof rawAgentContent}`);
    throw new Error("Invalid content type from agent for saving to blob.");
  }

  try {
    // Step 1: Check if content is just the placeholder
    if (rawAgentContent.trim() === "__GENERATING_NEWSLETTER_CONTENT__") {
      console.warn(`[saveNewsletterToBlob] Final content is STILL placeholder — skipping overwrite!`);
      return;
    } else {
      console.log(`[saveNewsletterToBlob] Content is valid — proceeding to overwrite.`);
    }

    // Step 2: Delete the existing blob to force CDN cache eviction
    try {
      await del(blobKey, { token: NEWSLETTER_READ_WRITE_TOKEN });
      console.log(`[Inngest] Deleted old blobKey before overwrite: ${blobKey}`);
    } catch (delError) {
      console.warn(`[Inngest] Could not delete old blob (may not exist yet):`, delError);
    }

    // Step 3: Upload new content (without random suffix!)
    const blob = await put(blobKey, rawAgentContent, {
      access: "public",
      contentType: "text/markdown",
      token: NEWSLETTER_READ_WRITE_TOKEN,
      allowOverwrite: true,
      addRandomSuffix: false,
    });

    // Step 4: Log and return
    console.log(`[Inngest] Successfully saved final blob for slug ${slug}`);
    console.log(`[Inngest] Content preview:`, rawAgentContent.slice(0, 200));
    console.log(`[Inngest] Blob URL: ${blob.url}`);
    return blob;

  } catch (error) {
    console.error(`[Inngest] Error saving to blob for slug ${slug}:`, error);
    throw error;
  }
}

// Write the placeholder blob first - solve stuck frontend page stuck on generating issue
async function writeInitialPlaceholderBlob(blobKey: string, slug: string) {
  try {
    const blob = await put(blobKey, "__GENERATING_NEWSLETTER_CONTENT__", {
      access: "public",
      contentType: "text/markdown",
      token: NEWSLETTER_READ_WRITE_TOKEN,
      allowOverwrite: true,
      addRandomSuffix: false, // to solve known behaviour in vercel blob storage where the same blobKey is not overwritten
    });
    console.log(`[Inngest] Placeholder blob created for slug ${slug}`);
    console.log(`[writeInitialPlaceholderBlob] Writing placeholder to blobKey: ${blobKey}`);
    return blob;
  } catch (error) {
    console.error(`[Inngest] Error writing initial placeholder blob for slug ${slug}:`, error);
    throw error;
  }
}
