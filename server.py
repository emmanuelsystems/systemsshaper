from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
from notion_client import Client
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MCP Notion Integration")

# Initialize clients
notion = Client(auth=os.getenv("NOTION_API_KEY"))
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

class NotionPage(BaseModel):
    title: str
    prompt: str
    date: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "ok", "message": "MCP Server is running"}

@app.post("/create-page")
async def create_page(page: NotionPage):
    try:
        # Format date or use current date
        page_date = page.date if page.date else datetime.now().isoformat()
        
        # Generate content using GPT
        completion = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates well-structured, detailed content."},
                {"role": "user", "content": page.prompt}
            ]
        )
        generated_content = completion.choices[0].message.content

        # Create the page in Notion
        new_page = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": page.title
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": page_date
                    }
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": generated_content
                                }
                            }
                        ]
                    }
                }
            ]
        )
        return {
            "status": "success", 
            "page_id": new_page.id,
            "content_preview": generated_content[:200] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        # Test both Notion and OpenAI connections
        notion.databases.retrieve(NOTION_DATABASE_ID)
        openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "notion_connection": "ok",
            "openai_connection": "ok",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
