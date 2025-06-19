import { NextResponse } from 'next/server';
import { inngest } from '@/inngest/client';
import { put, head } from "@vercel/blob";

const NEWSLETTER_PLACEHOLDER = "__GENERATING_NEWSLETTER_CONTENT__";

interface CachedApiResponse {
  status?: 'generating' | 'completed' | 'error';
  content?: string;
  source?: 'blob' | 'cache';
  blobUrl?: string;
  message?: string;
  error?: string;
}

// In-memory cache for API responses
const apiResponseCache = new Map<string, { timestamp: number; data: CachedApiResponse }>();

export async function GET(
  request: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  if (!slug) {
    return NextResponse.json({ error: 'Slug is required' }, { status: 400 });
  }

  const NEWSLETTER_READ_WRITE_TOKEN = process.env.NEWSLETTER_READ_WRITE_TOKEN;
  if (!NEWSLETTER_READ_WRITE_TOKEN) {
    console.error('NEWSLETTER_READ_WRITE_TOKEN environment variable is not set');
    return NextResponse.json({ error: 'Server config error: missing token' }, { status: 500 });
  }

  const blobKey = `newsletters/${slug}.md`;

  // Use cache if recent
  const cachedApiResponse = apiResponseCache.get(slug);
  if (cachedApiResponse && (Date.now() - cachedApiResponse.timestamp < 60000)) {
    if (cachedApiResponse.data.status === 'generating') {
      return NextResponse.json(cachedApiResponse.data);
    }
  }

  try {
    const existingBlob = await head(blobKey, { token: NEWSLETTER_READ_WRITE_TOKEN }).catch(() => null);

    if (existingBlob) {
      // Blob exists but we don’t know if it's ready — frontend will fetch and decide
      const responseData: CachedApiResponse = {
        status: 'generating',
        blobUrl: existingBlob.url,
        message: 'Newsletter is generating (blob exists but may be placeholder).'
      };
      apiResponseCache.set(slug, { timestamp: Date.now(), data: responseData });
      return NextResponse.json(responseData);
    }

    // Extract topics from slug
    let topics: string[] = [];
    const datePattern = /^(\d{4}-\d{2}-\d{2})-/;
    const dateMatch = slug.match(datePattern);
    if (dateMatch && dateMatch[1]) {
      const encodedTopicsPart = slug.substring(dateMatch[0].length);
      if (encodedTopicsPart) {
        topics = encodedTopicsPart
          .split('~')
          .map(t => decodeURIComponent(t.replace(/\+/g, ' ')))
          .filter(topic => topic !== '');
      }
    }

    if (topics.length === 0) {
      return NextResponse.json({ error: 'No valid topics found in slug.' }, { status: 400 });
    }

    // Step 1: Write placeholder blob
    const placeholderBlob = await put(blobKey, NEWSLETTER_PLACEHOLDER, {
      access: "public",
      contentType: "text/markdown",
      token: NEWSLETTER_READ_WRITE_TOKEN,
    });

    // Step 2: Trigger Inngest workflow
    await inngest.send({
      name: "newsletter/generate.requested",
      data: { topics, slug, blobKey: placeholderBlob.pathname },
    });

    const responseData: CachedApiResponse = {
      status: 'generating',
      blobUrl: placeholderBlob.url,
      message: 'Newsletter generation started.'
    };
    apiResponseCache.set(slug, { timestamp: Date.now(), data: responseData });
    return NextResponse.json(responseData);

  } catch (error) {
    console.error("Error in newsletter API route:", error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to process newsletter request.';
    return NextResponse.json({
      error: errorMessage,
      status: 'error',
      blobUrl: undefined,
      content: undefined,
      source: undefined
    }, { status: 500 });
  }
}

// Required for Vercel serverless edge functions
export const runtime = 'nodejs';
