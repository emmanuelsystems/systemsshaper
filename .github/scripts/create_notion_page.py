import os
import subprocess
from datetime import datetime
from notion_client import Client
import re

def extract_database_id(url_or_id):
    """Extract database ID from a Notion URL or return the ID if already in correct format."""
    # If it's a URL, extract the ID
    if 'notion.so' in url_or_id:
        match = re.search(r'([a-f0-9]{32}|\w{8}-\w{4}-\w{4}-\w{4}-\w{12})', url_or_id)
        if match:
            return match.group(1)
    return url_or_id

def get_commit_info():
    try:
        commit_msg = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()
        author = subprocess.check_output(['git', 'log', '-1', '--pretty=%an']).decode('utf-8').strip()
        files = subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD']).decode('utf-8').strip()
        return {
            'message': commit_msg,
            'author': author,
            'files': files
        }
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit info: {e}")
        return None

def create_notion_page():
    notion_token = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')

    if not notion_token or not database_id:
        print("Error: Missing required environment variables")
        print(f"NOTION_API_KEY: {'Set' if notion_token else 'Missing'}")
        print(f"NOTION_DATABASE_ID: {'Set' if database_id else 'Missing'}")
        return

    try:
        print(f"Connecting to Notion with token prefix: {notion_token[:6]}...")
        notion = Client(auth=notion_token)
        
        # Extract and format database ID
        original_id = database_id
        database_id = extract_database_id(database_id)
        print(f"Original database ID/URL: {original_id}")
        print(f"Extracted database ID: {database_id}")
        
        # Test database access
        try:
            print(f"Attempting to access database: {database_id}")
            db = notion.databases.retrieve(database_id)
            print("Successfully connected to database!")
            print(f"Database properties: {list(db['properties'].keys())}")
        except Exception as e:
            print(f"Error accessing database: {e}")
            print("\nPlease check:")
            print("1. The database ID is correct")
            print("2. The integration has been added to the database's Share settings")
            print("3. The integration has the necessary permissions")
            print("\nDebug info:")
            print(f"- Database ID format: {'Valid' if re.match(r'^[a-f0-9]{32}$', database_id) else 'Invalid'}")
            print(f"- Token format: {'Valid' if notion_token.startswith('ntn_') else 'Invalid'}")
            return

        commit_info = get_commit_info()
        if not commit_info:
            print("Error: Could not get commit information")
            return

        # Create the page
        new_page = {
            "parent": {"database_id": database_id},
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": f"Commit: {commit_info['message']}"
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                },
                "Author": {
                    "rich_text": [
                        {
                            "text": {
                                "content": commit_info['author']
                            }
                        }
                    ]
                },
                "Files": {
                    "rich_text": [
                        {
                            "text": {
                                "content": commit_info['files']
                            }
                        }
                    ]
                }
            }
        }

        response = notion.pages.create(**new_page)
        print(f"Successfully created Notion page for commit: {commit_info['message']}")
        return response

    except Exception as e:
        print(f"Error creating Notion page: {e}")
        raise

if __name__ == "__main__":
    create_notion_page()
