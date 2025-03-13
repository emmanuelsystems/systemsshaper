import os
import subprocess
from datetime import datetime
from notion_client import Client

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
        
        # Test database access first
        try:
            print(f"Attempting to access database: {database_id}")
            db = notion.databases.retrieve(database_id)
            print("Successfully connected to database!")
            print(f"Database properties: {list(db['properties'].keys())}")
        except Exception as e:
            print(f"Error accessing database: {e}")
            print("Please check:")
            print("1. The database ID is correct")
            print("2. The integration has been added to the database's Share settings")
            print("3. The integration has the necessary permissions")
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
