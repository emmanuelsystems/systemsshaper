import os
import subprocess
from datetime import datetime
from notion_client import Client
import re

def test_notion_connection(notion, database_id):
    """Test basic Notion API connectivity."""
    try:
        print("\nTesting database access...")
        db = notion.databases.retrieve(database_id)
        print("✓ Successfully accessed database!")
        print(f"Title: {db['title'][0]['text']['content'] if db['title'] else 'Untitled'}")
        print(f"Properties: {list(db['properties'].keys())}")
        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nPlease verify:")
        print("1. You've shared the database with the integration:")
        print("   - Open the database")
        print("   - Click Share in the top right")
        print("   - Click 'Add connections'")
        print("   - Search for 'GitHub Commits Integration'")
        print("   - Click Invite")
        print("\n2. The database has these properties:")
        print("   - Title (type: title)")
        print("   - Files (type: rich text)")
        print("   - auth (type: rich text)")
        print("   - date (type: date)")
        return False

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
        print(f"Connecting to Notion with token: {notion_token[:6]}...")
        notion = Client(auth=notion_token)
        
        # Clean up database ID (remove any URL parts)
        if 'notion.so' in database_id or 'notion.site' in database_id:
            matches = re.findall(r'[a-f0-9]{32}', database_id)
            if matches:
                database_id = matches[0]
        
        # Test database access
        if not test_notion_connection(notion, database_id):
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
                "date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                },
                "auth": {
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
        print(f"\n✓ Successfully created Notion page for commit: {commit_info['message']}")
        return response

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    create_notion_page()
