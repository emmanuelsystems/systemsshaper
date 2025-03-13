# GPT-to-Notion Integration

Automatically creates Notion pages from GitHub commits.

## Features
- Creates a new Notion page for each commit
- Includes commit message, author, and changed files
- Uses GitHub Actions for automation
- Simple and reliable integration
- Supports various database ID formats
- Detailed debug information
- Improved error handling

## Setup
1. Create a Notion integration at notion.so/my-integrations
2. Share your target database with the integration
3. Set up GitHub repository secrets:
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`

## Database Requirements
- Title property (default)
- Date property
- Author property (Text)
- Files property (Text)
