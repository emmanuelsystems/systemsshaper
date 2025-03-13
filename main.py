import os
from dotenv import load_dotenv
from notion_client import Client
import openai
from datetime import datetime

# Load environment variables
load_dotenv()

class NotionGPTIntegration:
    def __init__(self):
        # Initialize API clients
        self.notion = Client(auth=os.getenv("NOTION_API_KEY"))
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")

    def generate_content(self, prompt):
        """Generate content using GPT"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content

    def create_notion_page(self, title, content):
        """Create a new page in Notion database"""
        new_page = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": title}}]
                },
                "Date": {
                    "date": {"start": datetime.now().date().isoformat()}
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": content}}]
                    }
                }
            ]
        }
        return self.notion.pages.create(**new_page)

    def process_request(self, title, prompt):
        """Process a complete request"""
        content = self.generate_content(prompt)
        return self.create_notion_page(title, content)

def main():
    try:
        integration = NotionGPTIntegration()
        
        # Example usage
        title = "Sample GPT Generated Note"
        prompt = "Write a brief summary about AI and productivity tools."
        
        result = integration.process_request(title, prompt)
        print(f"Successfully created page with ID: {result['id']}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
