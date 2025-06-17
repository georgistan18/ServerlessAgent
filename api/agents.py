import os
import sys

from dotenv import load_dotenv
load_dotenv(".env.local")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner, WebSearchTool, ModelSettings

# Load OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("OPENAI_API_KEY not found in environment variables", file=sys.stderr)
    raise ValueError("OPENAI_API_KEY must be set")

# Define request schemas
class TopicsRequest(BaseModel):
    topics: list[str]

class FormatRequest(BaseModel):
    raw_content: str
    topics: list[str]

# Initialize FastAPI app with root path for Vercel
app = FastAPI(title="AI Company Analysis Agents", root_path="/api/agents")

@app.get("/ping")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "openai_api_key_set": bool(OPENAI_API_KEY),
        "vercel_url": os.getenv("VERCEL_URL", "not set"),
        "python_version": sys.version,
        "agents_imported": "agents" in sys.modules,
    }

# Research Agent: Searches web and generates company analysis
research_agent = Agent(
    name="Research Agent",
    model="gpt-4.1",
    instructions=(
        #todo: preventhallucination
        #perplexity
        "You are an AI assistant that creates comprehensive company analysis reports.\n\n"
        "Your process:\n"
        "1. Search the web comprehensively for information about the given company:\n"
        "   - Company overview and history\n"
        "   - Recent financial performance and stock data\n"
        "   - Latest news and developments\n"
        "   - Market position and competitors\n"
        "   - Key products/services\n"
        "   - Leadership team and organizational structure\n"
        "   - Future outlook and strategic initiatives\n"
        "2. Perform multiple searches with different query variations to ensure broad coverage\n"
        "3. Prioritize recent information (last 30 days) but include historical context\n"
        "4. Look for both general news and specific expert analysis\n"
        "5. If initial results are insufficient, refine your search queries and search again\n\n"
        "If there is no company under the name provided, please do not hallucinate and clearly state 'Company could not be found'"
        "Your output structure:\n"
        "**[Company Name] - Comprehensive Risk Analysis**\n\n"
        "*[One impactful sentence summarizing the company's current position and outlook]*\n\n"
        "**Executive Summary**\n"
        "A concise 2-3 paragraph overview that:\n"
        "- Summarizes the company's core business and market position\n"
        "- Highlights recent significant developments\n"
        "- Outlines key challenges and opportunities\n\n"
        "**Company Overview**\n"
        "- Brief history and founding story\n"
        "- Core business model and main products/services\n"
        "- Key markets and customer segments\n\n"
        "**Recent Developments**\n"
        "- Latest news and announcements\n"
        "- Recent financial performance\n"
        "- Strategic initiatives and partnerships\n\n"
        "**Market Position**\n"
        "- Competitive landscape\n"
        "- Market share and industry standing\n"
        "- Key differentiators\n\n"
        "**Leadership & Organization**\n"
        "- Key executives and their backgrounds\n"
        "- Organizational structure\n"
        "- Corporate culture highlights\n\n"
        "**Future Outlook**\n"
        "- Growth strategies and initiatives\n"
        "- Potential challenges and risks\n"
        "- Market opportunities\n\n"
        "**Key Metrics & Financials**\n"
        "- Recent financial highlights\n"
        "- Important KPIs\n"
        "- Stock performance (if public)\n\n"
        "Use clear, professional language throughout.\n"
        "Focus on providing actionable insights and a balanced view of the company's position."
        "\n\nAfter your full company analysis, include the following section:\n\n"
        "**Structured Data Summary**\n"
        "Return a dictionary-like block that provides the following fields if possible:\n"
        "- registration_year: Year the company was officially registered.\n"
        "- status: Current legal status of the company (active, inactive, bankrupt, etc.)\n"
        "- last_year_report: Last year in which a public business report was avaiblable.\n"
        "- market_presence: Describe how well-known the company is in its market.\n"
        "- dealer_network: Size and scope of the company's distributor or reseller network (e.g. '20 authorized delaers across Europe').\n"
        "- revenue_trends: Summary of recent revenue growth or decline.\n"
        "- top_product_revenue_share: % of total revenue coming from the top-selling product.\n"
        "- product_lines: Main product or service categories the company offers.\n"
        "- top_50_percent_revenue: List of products or clients that together make up the top 50% of the company's revenue.\n"
        "- num_clients: Estimated number of active clients or buyers.\n"
        "- top3_clients_share: % of revenue that comes from the top 3 clients.\n"
        "- info_sources: List of key websites or sources you used to extract the above data (e.g., 'crunchbase.com', 'company investor page', 'listafirme.ro', 'bloomberg.com', 'opencorporates.com' - but do not be limited to these examples)\n\n"
        "If any value is unknown or not found, clearly write 'Unknown'.\n"
        "Return the summary inside a code block like this:\n"
        "```json\n"
        "{\n"
        "  \"registration_year\": 2010,\n"
        "  \"status\": \"active\",\n"
        "  ...\n"
        "}\n"
        "```"
        "6. If the first 1–2 sources do not contain enough information, look for alternative sources such as:\n"
        "   - Industry publications and reports\n"
        "   - Company investor relations pages\n"
        "   - Analyst insights on financial portals\n"
        "   - Global distributor lists or supplier directories\n"
        "7. If you still cannot find any data, state 'Unknown' but explain what sources were checked.\n"

    ),
    tools=[ WebSearchTool() ]
)

# Formatting Agent: Transforms content into polished markdown
formatting_agent = Agent(
    name="Formatting Agent", 
    # model="gpt-4.1",
    model='o3',
    instructions=(
        "You are an expert editor and markdown formatter who transforms research content into beautiful, readable newsletters.\n\n"
        "Your task:\n"
        "1. Take the provided research content and transform it into a polished newsletter\n"
        "2. Apply professional markdown formatting:\n"
        "   - Use **bold** for the main title\n"
        "   - Use *italics* for the one-sentence summary\n"
        "   - Structure content with clear hierarchical headers (##, ###)\n"
        "   - Create visually appealing lists with bullet points or numbers\n"
        "   - Add pull quotes using > blockquote syntax for key insights\n"
        "   - Use horizontal rules (---) to separate major sections\n"
        "   - Format links properly: [text](url)\n"
        "   - Add emphasis with **bold** and *italic* text strategically\n"
        "3. Enhance readability:\n"
        "   - Break up long paragraphs\n"
        "   - Add spacing between sections\n"
        "   - Create clear visual hierarchy\n"
        "   - Ensure smooth flow between sections\n"
        "4. Maintain all the original content and insights\n"
        "5. The output should be publication-ready markdown that looks professional when rendered\n\n"
        "Transform the content into an engaging, visually appealing newsletter while preserving all information."
    ),
    tools=[]
)

@app.post("/research")
async def generate_research(request: TopicsRequest):
    topics = request.topics
    if not topics:
        return {"error": "No topics provided."}
    
    # Get current date and yesterday for fresh news focus
    from datetime import datetime, timedelta
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_str = today.strftime("%B %d, %Y")
    yesterday_str = yesterday.strftime("%B %d, %Y")
    
    # Compose a prompt by joining the topics
    company_name = ", ".join(topics)
    user_prompt = (
        f"Today is {today_str}. I need you to research and analyze {company_name} comprehensively. "
        f"IMPORTANT: Include a structured JSON at the end with key data points for analysis. "
        f"Focus on recent developments from the last 30 days (since {yesterday_str}), "
        f"but include historical context too."
    )
    
    # Run the research agent
    result = await Runner.run(research_agent, user_prompt)
    raw_content = result.final_output

    import re
    import json

    # extract json from markdown
    def extract_json_from_markdown(text):
        """
        Extracts the last JSON block from the markdown test (enclosed in ```json ... ```)
        Returns a Python dict or None if parsing fails
        This parsed object is then available to be processed by rules
        """
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    structured_data = extract_json_from_markdown(raw_content)

    return {
        "content": raw_content,
        "structured_data": structured_data,
        "flags": None,  # APPLY RULE LOGIC HERE LATER
        "error": None if structured_data else "Structured JSON could not be parsed."
    }
    # apply rules to structured data


@app.post("/format")
async def format_newsletter(request: FormatRequest):
    raw_content = request.raw_content
    
    company_name = request.topics[0]
    
    
    if not raw_content:
        return {"error": "No content provided."}
    
    # Create formatting prompt
    user_prompt = f"Transform this research content into a beautifully formatted company analysis report for {company_name}. Apply professional markdown formatting:\n\n{raw_content}"
    
    # Run the formatting agent
    result = await Runner.run(formatting_agent, user_prompt)
    formatted_content = result.final_output
    
    return {"content": formatted_content}

# IMPORTANT: Handler for Vercel serverless functions
# Vercel's Python runtime will automatically handle FastAPI apps
# No additional configuration needed - just export the 'app' variable
