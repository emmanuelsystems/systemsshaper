import os
import subprocess
from datetime import datetime
from notion_client import Client

def format_database_id(db_id):
    # Try different formats of the database ID
    formats = [
        db_id,  # Original
        db_id.replace('-', ''),  # No hyphens
        '-'.join([db_id[:8], db_id[8:12], db_id[12:16], db_id[16:20], db_id[20:]]),  # With hyphens
        db_id.split('?')[0]  # Remove query params
    ]
    return formats

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

        # Try different database ID formats
        db_formats = format_database_id(database_id)
        success = False

        for db_id in db_formats:
            try:
                print(f"Trying database ID format: {db_id}")
                # Test if we can access the database
                notion.databases.retrieve(db_id)
                database_id = db_id
                success = True
                print(f"Successfully connected to database with ID: {db_id}")
                break
            except Exception as e:
                print(f"Failed with format {db_id}: {str(e)}")
                continue

        if not success:
            print("Could not connect to database with any ID format")
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
