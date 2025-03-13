import os
import subprocess
from datetime import datetime
from notion_client import Client
import re

def test_notion_connection(notion, database_id):
    """Test basic Notion API connectivity."""
    try:
        # Try to list all users with access to verify token works
        users = notion.users.list()
        print("\n✓ Successfully connected to Notion API!")
        print(f"Bot user: {users.get('bot', {}).get('owner', {}).get('name', 'Unknown')}")
        
        # Try to access the database directly
        try:
            db = notion.databases.retrieve(database_id)
            print("\n✓ Successfully accessed database!")
            print(f"Title: {db['title'][0]['text']['content'] if db['title'] else 'Untitled'}")
            print(f"Properties: {list(db['properties'].keys())}")
            return True
        except Exception as e:
            print(f"\n✗ Error accessing database: {str(e)}")
            print("\nPlease verify:")
            print("1. The database ID is correct")
            print("2. The integration has been added to the database via Share > Add connections")
            print("3. The database has the required properties:")
            print("   - Title (type: title)")
            print("   - Date (type: date)")
            print("   - Author (type: text)")
            print("   - Files (type: text)")
            return False
            
    except Exception as e:
        print(f"\n✗ Error connecting to Notion: {e}")
        print("\nPlease verify:")
        print("1. The integration token is correct")
        print("2. The integration has these capabilities enabled:")
        print("   - Read content")
        print("   - Update content")
        print("   - Insert content")
        print("   - No user information")
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
        print(f"Connecting to Notion with token prefix: {notion_token[:6]}...")
        notion = Client(auth=notion_token)
        
        # Clean up database ID (remove any URL parts)
        if 'notion.so' in database_id or 'notion.site' in database_id:
            matches = re.findall(r'[a-f0-9]{32}', database_id)
            if matches:
                database_id = matches[0]
        
        # Test connection and database access
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
        print(f"\n✓ Successfully created Notion page for commit: {commit_info['message']}")
        return response

    except Exception as e:
        print(f"\n✗ Error creating Notion page: {e}")
        raise

if __name__ == "__main__":
    create_notion_page()
