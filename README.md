# GPT-to-Notion Integration

A FastAPI-based MCP (Message Control Program) server that integrates with Notion to create and manage pages.

## Setup

1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the following values:
     - `NOTION_API_KEY`: Get from [Notion Integrations](https://notion.so/my-integrations)
     - `NOTION_DATABASE_ID`: Get from your Notion database URL

3. Notion Database Requirements:
   - Must have a "Title" property (default)
   - Must have a "Date" property (type: date)
   - Database must be shared with your Notion integration

## Running the Server

```bash
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### GET /
Health check endpoint to verify server status.

### POST /create-page
Create a new page in your Notion database.

Request body:
```json
{
    "title": "Page Title",
    "date": "2025-03-13T00:00:00Z"  // Optional, defaults to current time
}
```

### GET /health
Check connection status with Notion API.

## Dependencies

- notion-client (>=2.0.0)
- fastapi (>=0.109.0)
- uvicorn (>=0.27.0)
- python-dotenv (>=1.0.0)
