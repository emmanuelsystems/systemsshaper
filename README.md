# GPT-to-Notion Integration

A FastAPI-based MCP (Message Control Program) server that integrates with Notion to create and manage pages. Features automatic GitHub Actions integration that creates Notion pages for each commit with GPT-powered summaries.

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
     - `OPENAI_API_KEY`: Your OpenAI API key

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
    "prompt": "Content generation prompt for GPT",
    "date": "2025-03-13T00:00:00Z"  // Optional, defaults to current time
}
```

### GET /health
Check connection status with Notion API and OpenAI API.

## GitHub Actions Integration

This project includes automatic Notion page creation for each commit using GitHub Actions. When you push to the repository:

1. A new Notion page is created automatically
2. GPT analyzes your commit and generates a detailed summary
3. The page includes:
   - Commit information (hash, author, date)
   - List of changed files
   - GPT-generated analysis of changes

### Required GitHub Secrets

Add these secrets to your repository:
- `NOTION_API_KEY`: Your Notion integration token
- `NOTION_DATABASE_ID`: Your Notion database ID
- `OPENAI_API_KEY`: Your OpenAI API key

## Dependencies

- notion-client (>=2.0.0)
- openai (>=1.0.0)
- python-dotenv (>=1.0.0)
- fastapi (>=0.109.0)
- uvicorn (>=0.27.0)
