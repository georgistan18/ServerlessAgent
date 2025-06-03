import { inngest } from "./client";
import { put } from "@vercel/blob";
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

// Main Inngest function with multi-step workflow
export const generateNewsletter = inngest.createFunction(
  { id: "generate-newsletter" },
  { event: "newsletter/generate.requested" },
  async ({ event, step }: { event: { data: NewsletterGenerateRequestedData }; step: unknown }) => {
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

    // Step 1: Call Python Agent
    const rawAgentContentUnknown = await step.run("call-python-agent", () => callPythonAgent(topics, slug));
    if (typeof rawAgentContentUnknown !== 'string') {
      throw new Error('Python agent did not return a string');
    }
    const rawAgentContent = rawAgentContentUnknown;

    // Step 2: Format Newsletter with Markdown Agent
    const formattedContentUnknown = await step.run("format-newsletter", () => formatNewsletter(rawAgentContent, topics, slug));
    if (typeof formattedContentUnknown !== 'string') {
      throw new Error('Formatting agent did not return a string');
    }
    const formattedContent = formattedContentUnknown;

    // Step 3: Save Newsletter to Blob
    const finalBlobUnknown = await step.run("save-to-blob", () => saveNewsletterToBlob(blobKey, formattedContent, slug));
    if (!finalBlobUnknown || typeof finalBlobUnknown !== 'object' || typeof (finalBlobUnknown as { url?: unknown }).url !== 'string') {
      throw new Error('Blob result missing url');
    }
    const finalBlob = finalBlobUnknown as { url: string };

    return { url: finalBlob.url, message: `Newsletter generated and saved for ${slug}` };
  }
);

// --- Step implementations below ---

async function callPythonAgent(topics: string[], slug: string) {
  console.log(`[Inngest] Calling Python research agent for slug ${slug} with topics:`, topics);
  
  // Use Vercel URL in production, fallback to localhost for development
  const pythonAgentUrl = process.env.VERCEL_URL 
    ? `https://${process.env.VERCEL_URL}/api/agents`
    : 'http://localhost:8000';
  
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
    
    if (!content) {
      throw new Error('Research agent returned no content');
    }

    console.log(`[Inngest] Research agent success for slug ${slug}. Content length: ${content.length}`);
    return content;
  } catch (error) {
    console.error(`[Inngest] Research agent error for slug ${slug}:`, error);
    throw error;
  }
}

async function formatNewsletter(rawContent: string, topics: string[], slug: string) {
  console.log(`[Inngest] Calling formatting agent for slug ${slug}`);
  
  // Use Vercel URL in production, fallback to localhost for development
  const pythonAgentUrl = process.env.VERCEL_URL 
    ? `https://${process.env.VERCEL_URL}/api/agents`
    : 'http://localhost:8000';
  
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

    console.log(`[Inngest] Formatting agent success for slug ${slug}. Content length: ${content.length}`);
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
    const blob = await put(blobKey, rawAgentContent, {
      access: "public",
      contentType: "text/markdown",
      token: NEWSLETTER_READ_WRITE_TOKEN,
      allowOverwrite: true,
    });
    console.log(`[Inngest] Newsletter saved to blob for slug ${slug}. URL: ${blob.url}`);
    return blob;
  } catch (error) {
    console.error(`[Inngest] Error saving to blob for slug ${slug}:`, error);
    throw error;
  }
}
