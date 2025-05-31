import os
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner, WebSearchTool, ModelSettings

# Note: You'll need to install these via requirements.txt
# from agents import Agent, Runner, WebSearchTool

# Load OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "OPENAI_API_KEY must be set"

# Define request schemas
class TopicsRequest(BaseModel):
    topics: list[str]

class FormatRequest(BaseModel):
    raw_content: str
    topics: list[str]

# Initialize FastAPI
app = FastAPI(title="AI Newsletter Agents")

# First Agent: Research and Content Generation
research_agent = Agent(
    name="Research Agent",
    model="gpt-4.1", # This is OpenAI's latest model, don't change it. We will use it with the default temperature settings.
    instructions=(
        "You are an AI assistant that creates insightful, well-connected newsletters on a set of given topics.\n\n"
        "Your process:\n"
        "1. Search the web comprehensively for the latest news and information on each one of the given topics individually:\n"
        "   - Perform multiple searches with different query variations to ensure broad coverage\n"
        "   - Look for recent articles (prioritize content from the last 7-30 days)\n"
        "   - Search for both general news and specific expert analysis\n"
        "   - If initial results are insufficient, refine your search queries and search again\n"
        "2. Repeat the same approach to search for the other topics given\n"
        "3. For each topic, analyze the articles to identify connections, patterns, and relationships between them.\n"
        "4. Create a cohesive narrative that explains how these articles relate to each other.\n\n"
        "Your output structure:\n"
        "**[Create a compelling title that captures the essence of how all topics connect]**\n\n"
        "*[Write one impactful sentence that summarizes the key relationship or theme connecting all the topics]*\n\n"
        "**Executive Summary**\n"
        "Start with a compelling 2-3 paragraph summary that:\n"
        "- Identifies the main themes across all articles\n"
        "- Explains the connections and relationships between different pieces of information\n"
        "- Highlights why these connections matter\n"
        "- Provides context for how these topics intersect\n\n"
        "**Key Insights**\n"
        "- List 3-5 major insights that emerge from analyzing these articles together\n"
        "- Explain how different sources complement or contradict each other\n\n"
        "**Detailed Analysis**\n"
        "For each major theme or connection:\n"
        "- Provide specific examples from the articles\n"
        "- Include relevant facts, figures, and quotes\n"
        "- Cite sources properly\n\n"
        "**Conclusion**\n"
        "Synthesize everything into a forward-looking paragraph about implications and trends.\n\n"
        "Use clear, engaging language throughout.\n"
        "Focus on creating a narrative that shows how these topics interconnect rather than just listing summaries."
    ),
    tools=[ WebSearchTool() ]
)

# Second Agent: Markdown Formatting and Enhancement
formatting_agent = Agent(
    name="Formatting Agent", 
    model="o3",
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
    tools=[]  # No tools needed for formatting
)

@app.post("/research")
async def generate_research(request: TopicsRequest):
    topics = request.topics
    if not topics:
        return {"error": "No topics provided."}
    
    # Compose a prompt by joining the topics
    topics_list = ", ".join(topics)
    user_prompt = f"Research and analyze these topics comprehensively: {topics_list}. Find connections between them and create a detailed report."
    
    # Run the research agent
    result = await Runner.run(research_agent, user_prompt)
    raw_content = result.final_output
    
    return {"content": raw_content}

@app.post("/format")
async def format_newsletter(request: FormatRequest):
    raw_content = request.raw_content
    topics = request.topics
    
    if not raw_content:
        return {"error": "No content provided."}
    
    # Create formatting prompt
    topics_list = ", ".join(topics)
    user_prompt = f"Transform this research content into a beautifully formatted newsletter about {topics_list}. Apply professional markdown formatting:\n\n{raw_content}"
    
    # Run the formatting agent
    result = await Runner.run(formatting_agent, user_prompt)
    formatted_content = result.final_output
    
    return {"content": formatted_content}

# Vercel serverless function handler
handler = app 
