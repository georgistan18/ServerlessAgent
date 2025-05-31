# Serverless Agents - AI Newsletter Generator

A Next.js application with Inngest serverless functions and FastAPI Python agents for generating AI-powered newsletters.

## 🚀 Local Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key

### 1. Install Dependencies

**Frontend (Next.js + Inngest):**
```bash
npm install
```

**Backend (Python FastAPI):**
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env.local` file in the root directory:

```bash
# OpenAI API Key (required for agents)
OPENAI_API_KEY=your_openai_api_key_here

# Inngest Configuration (optional for local dev)
INNGEST_SIGNING_KEY=your_inngest_signing_key

# Vercel Blob (for newsletter storage)
BLOB_READ_WRITE_TOKEN=your_vercel_blob_token
```

### 3. Start Development Servers

**Terminal 1 - FastAPI Python Agent:**
```bash
uvicorn api.agents:app --reload --reload-dir api --port 8000
```

Server will run at: http://localhost:8000

**Terminal 2 - Next.js Frontend:**
```bash
npm run dev
```

Frontend will run at: http://localhost:3000

**Terminal 3 - Inngest Dev Server:**
```bash
npx inngest-cli@latest dev --no-discovery -u http://localhost:3000/api/inngest
```

Inngest dashboard will run at: http://localhost:8288

### 4. Testing the System

1. **Test FastAPI Agent directly:**
   ```bash
   curl -X POST http://localhost:8000/newsletter \
     -H "Content-Type: application/json" \
     -d '{"topics": ["AI", "Climate Tech"]}'
   ```

2. **Test Inngest Functions:**
   - Visit http://localhost:8288 for Inngest dashboard
   - Trigger newsletter generation via your frontend or API

3. **Trigger Newsletter Generation:**
   ```typescript
   await inngest.send({
     name: "newsletter/submit",
     data: { topics: ["AI", "Startups"], userId: "test-user" }
   });
   ```

## 🏗️ Architecture

- **Frontend**: Next.js 15 with TypeScript
- **Serverless Functions**: Inngest for reliable workflow orchestration
- **AI Agents**: FastAPI with OpenAI Agents SDK + WebSearch
- **Storage**: Vercel Blob for generated newsletters
- **Deployment**: Vercel (both frontend and Python functions)

## 📁 Project Structure

```
├── src/
│   ├── app/
│   │   └── api/inngest/route.ts    # Inngest API endpoint
│   └── inngest/
│       ├── client.ts               # Inngest client config
│       └── functions.ts            # Newsletter generation workflow
├── api/
│   └── agents.py                   # FastAPI Python agents
├── requirements.txt                # Python dependencies
└── package.json                    # Node.js dependencies
```

## 🚢 Deployment

Deploy to Vercel with:

```bash
# Set environment variables
vercel env add OPENAI_API_KEY

# Deploy (Vercel automatically provides VERCEL_URL)
vercel --prod
```

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Inngest Documentation](https://www.inngest.com/docs)
- [OpenAI Agents SDK](https://github.com/openai/agents)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
