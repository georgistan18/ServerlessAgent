# Holds the RULES dictionary with prompt templates, criteria metadata, and maps everything together

import os
import sys

from dotenv import load_dotenv
load_dotenv(".env.local")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner, WebSearchTool, ModelSettings

# givve access to the rule evaluation and prompt templates
from .rules.rules_logic import RULES
from .rules.rule_engine import evaluate_rule

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
        "3. If you don't find the information required, sometimes it may be useful to search again for the company information by its legal name (for e.g. Veridion's legal name is Dataworks Research SRL and you can find the last financial report date by this name on listafirme.ro) or ultimately the company's parent company or subsidiaries\n. Include this information in the structured data summary if you found it."
        "4. Prioritize recent information (last 30 days) but include historical context\n"
        "5. Look for both general news and specific expert analysis\n"
        "6. If initial results are insufficient, refine your search queries and search again\n\n"
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
        "- last_report_year: Last year in which a public business report was avaiblable.\n"

        "- market_presence: Describe how well-known the company is in its market.\n"
        "- dealer_network: Size and scope of the company's distributor or reseller network (e.g. '20 authorized delaers across Europe').\n"
        "- revenue_trends: Summary of recent revenue growth or decline.\n"

        "- top_product_revenue_share: % of total revenue coming from the top-selling product.\n"
        "- product_lines: Main product or service categories the company offers.\n"

        "- top_50_percent_revenue: List of products or clients that together make up the top 50% of the company's revenue.\n"
        "- num_clients: Estimated number of active clients or buyers.\n"
        "- top3_clients_share: % of revenue that comes from the top 3 clients.\n"

        "- top_50_percent_cogs: Number of suppliers or products that account for the top 50% of the company’s Cost of Goods Sold (COGS).\n"
        "- top3_suppliers_share: Estimated combined share of purchases or COGS coming from the top three suppliers.\n"

        "- traceability_system: Description of whether the company uses tools like GPS, QR codes, RFID, or ERP systems for asset tracking.\n"
        "- methods: Technologies or operational procedures used to trace or track the location of financed or leased assets.\n"
        "- since: Year or period since the traceability system has been implemented.\n"

        "- esg_policy: Existence and description of any formal Environmental, Social, and Governance (ESG) policy or report.\n"
        "- certifications: ESG- or security-related certifications (e.g., ISO 14001, ISO 27001, SA8000).\n"
        "- incidents: Notable ESG violations, controversies, fines, or security breaches the company has faced.\n"

        "- credit_rating: Official rating (e.g. BBB, A-, etc.) from recognized agencies such as Moody's, S&P, or Fitch.\n"
        "- agency: Name of the credit rating agency that assigned the credit rating.\n"

        "- info_sources: List of key websites or source (websites, databases, filings) you used to extract the above data (e.g., 'crunchbase.com', 'company investor page', 'listafirme.ro', 'bloomberg.com', 'opencorporates.com' - but do not be limited to these examples)\n\n"
        "If any value is unknown or not found, clearly write 'Unknown'.\n"
        "Return the summary inside a code block like this:\n"
        "```json\n"
        "{\n"
        "  \"registration_year\": 2010,\n"
        "  \"status\": \"active\",\n"
        "  ...\n"
        "}\n"
        "```"
        "7. If the first 1–2 sources do not contain enough information, look for alternative sources such as:\n"
        "   - Industry publications and reports\n"
        "   - Company investor relations pages\n"
        "   - Analyst insights on financial portals\n"
        "   - Global distributor lists or supplier directories\n"
        "8. If you still cannot find any data, state 'Unknown' but explain what sources were checked.\n"

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

    # Combine into one string like: "manufacturer: Olympus"
    combined = " ".join(topics).strip().lower()

    # Determine entity type and name
    import re
    match = re.match(r"(manufacturer|dealer|asset):\s*(.+)", combined, re.IGNORECASE)
    if match:
        entity_type = match.group(1).lower()
        company_name = match.group(2).strip()
    else:
        # fallback if no prefix given
        entity_type = "manufacturer"
        company_name = combined

    from datetime import datetime, timedelta
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_str = today.strftime("%B %d, %Y")
    yesterday_str = yesterday.strftime("%B %d, %Y")

    user_prompt = (
        f"Today is {today_str}. I need you to research and analyze {company_name} as a {entity_type} company. "
        f"IMPORTANT: Include a structured JSON at the end with key data points for vetting. "
        f"Focus on recent developments from the last 30 days (since {yesterday_str}), "
        f"but include historical context too."
    )

    # Run the research agent
    result = await Runner.run(research_agent, user_prompt)
    raw_content = result.final_output

    import json
    import re
    def extract_json_from_markdown(text):
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    structured_data = extract_json_from_markdown(raw_content)

    if not structured_data:
        return {
            "content": raw_content,
            "structured_data": None,
            "flags": None,
            "risk_summary": None,
            "error": "Structured JSON could not be parsed."
        }

    # TODO: for now we only have manufacturer rules
    # later add logic for dealer / asset
    flags = {}
    explanations = []
    for key, rule in RULES.items():
        try:
            result = evaluate_rule(key, structured_data)
            flags[key] = result["flag"]
            explanation = result["prompt"].format(flag=result["flag"], **structured_data)
            explanations.append(f"### {rule['name']} ({result['flag']})\n{explanation}")
        except Exception as e:
            flags[key] = "Error"
            explanations.append(f"### {rule['name']} (Error)\n{str(e)}\n")

    summary_prompt = (
        "Based on the following company evaluation flags, write a markdown risk summary section explaining each risk in plain English. "
        "Use 🚩 for 'Review', ⚠️ for 'Monitor', ✅ for 'OK'. Format nicely with headers and bullet points if needed.\n\n"
    + "\n\n".join(explanations))

    summary_result = await Runner.run(formatting_agent, summary_prompt)
    risk_summary = summary_result.final_output

    return {
        "content": raw_content,
        "structured_data": structured_data,
        "flags": flags,
        "risk_summary": risk_summary,
        "error": None
    }

            
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
