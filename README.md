# GPT-to-Notion Integration

This project integrates OpenAI's GPT API with Notion, allowing you to automatically create and update Notion pages using GPT-generated content.

## Features
- Seamless integration between OpenAI's GPT API and Notion
- Automatic page creation and content generation
- Environment-based configuration for secure API key management

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
```

3. Run the script:
```bash
python main.py
```

## Requirements
- Python 3.8+
- OpenAI API key
- Notion API key and integration setup
- Notion database ID
