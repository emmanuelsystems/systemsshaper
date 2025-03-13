import os
import subprocess
from datetime import datetime
from notion_client import Client

def format_database_id(db_id):
    # Remove any query parameters
    db_id = db_id.split('?')[0]
    
    # Extract just the ID part if it's a full URL
    if 'notion.so' in db_id:
        db_id = db_id.split('/')[-1]
    
    # Remove any non-alphanumeric characters
    db_id = ''.join(c for c in db_id if c.isalnum())
    
    # Format with hyphens
    if len(db_id) == 32:
        return '-'.join([
            db_id[:8],
            db_id[8:12],
            db_id[12:16],
            db_id[16:20],
            db_id[20:]
        ])
    return db_id

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
        return

    try:
        notion = Client(auth=notion_token)
        commit_info = get_commit_info()

        if not commit_info:
            print("Error: Could not get commit information")
            return

        # Format the database ID
        print(f"Original database ID: {database_id}")
        database_id = format_database_id(database_id)
        print(f"Formatted database ID: {database_id}")

        # Test database access
        try:
            db = notion.databases.retrieve(database_id)
            print("Successfully connected to database!")
            print(f"Database properties: {list(db['properties'].keys())}")
        except Exception as e:
            print(f"Error accessing database: {e}")
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
