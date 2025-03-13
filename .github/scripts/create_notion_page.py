import os
import subprocess
from datetime import datetime
from notion_client import Client

def get_commit_info():
    """Get the latest commit information"""
    print("Getting commit information...")
    try:
        commit_msg = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
        author = subprocess.check_output(['git', 'log', '-1', '--pretty=%an']).decode('utf-8').strip()
        date = subprocess.check_output(['git', 'log', '-1', '--pretty=%aI']).decode('utf-8').strip()
        
        # Get list of changed files
        changed_files = subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD']).decode('utf-8').strip().split('\n')
        
        print(f"Found commit: {commit_msg} ({commit_hash})")
        return {
            'message': commit_msg,
            'hash': commit_hash,
            'author': author,
            'date': date,
            'changed_files': changed_files
        }
    except subprocess.CalledProcessError as e:
        print(f"Error getting git info: {str(e)}")
        raise

def create_notion_page(commit_info):
    """Create a new page in Notion with commit information."""
    try:
        notion = Client(auth=os.getenv('NOTION_API_KEY'))
        database_id = os.getenv('NOTION_DATABASE_ID')
        print(f"Using database ID: {database_id}")

        # Create the page
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
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
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Commit Hash: {commit_info['hash']}\n\n"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Author: {commit_info['author']}\n"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Files Changed:\n{commit_info['changed_files']}"
                                }
                            }
                        ]
                    }
                }
            ]
        )
        print(f"Successfully created Notion page with ID: {new_page['id']}")
        return new_page

    except Exception as e:
        print(f"Error creating Notion page: {str(e)}")
        raise

def main():
    """Main function to create a Notion page for the latest commit."""
    print("Starting Notion page creation...")
    try:
        # Get commit information
        commit_info = get_commit_info()
        print(f"Found commit: {commit_info['message']} ({commit_info['hash']})")

        # Create the Notion page
        create_notion_page(commit_info)
        print("Successfully created Notion page!")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
