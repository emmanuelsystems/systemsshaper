import os
import subprocess
from datetime import datetime
from notion_client import Client
import re

def test_notion_connection(notion):
    """Test basic Notion API connectivity."""
    try:
        # Try to search for the database
        results = notion.search(
            query="GitHub Commits",
            filter={
                "property": "object",
                "value": "database"
            }
        ).get("results", [])
        
        if results:
            print("\n✓ Successfully connected to Notion API!")
            print("Found databases:")
            for db in results:
                db_id = db["id"]
                title = db["title"][0]["text"]["content"] if db["title"] else "Untitled"
                print(f"- {title} (ID: {db_id})")
            return results
        else:
            print("\n✓ Connected to Notion API, but no matching databases found.")
            return []
            
    except Exception as e:
        print(f"\n✗ Error testing Notion connection: {e}")
        return []

def try_database_formats(db_id):
    """Try different formats of the database ID."""
    formats = []
    
    # If it's a URL, extract the ID
    if 'notion.so' in db_id or 'notion.site' in db_id:
        # Extract the ID from the end of the URL
        matches = re.findall(r'[a-f0-9]{32}', db_id)
        if matches:
            db_id = matches[0]
    
    # Remove any query parameters
    db_id = db_id.split('?')[0]
    
    # Original format (no hyphens)
    clean_id = ''.join(c for c in db_id if c.isalnum())
    formats.append(clean_id)
    
    # UUID format (with hyphens)
    if len(clean_id) == 32:
        uuid_format = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
        formats.append(uuid_format)
    
    # Notion's internal format (no hyphens)
    formats.append(clean_id.lower())
    
    return list(set(formats))  # Remove duplicates

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
        
        # First, test the basic API connection
        databases = test_notion_connection(notion)
        if not databases:
            print("\nPlease check:")
            print("1. The integration token is correct")
            print("2. The integration has the necessary capabilities enabled")
            print("3. The integration has been added to at least one database")
            return
            
        # Try to access the specific database
        db_formats = try_database_formats(database_id)
        print(f"Original database ID/URL: {database_id}")
        print(f"Trying formats: {db_formats}")
        
        success = False
        for db_id in db_formats:
            try:
                print(f"\nTrying database ID: {db_id}")
                db = notion.databases.retrieve(db_id)
                print("✓ Successfully connected to database!")
                print(f"Database title: {db['title'][0]['text']['content'] if db['title'] else 'Untitled'}")
                print(f"Database properties: {list(db['properties'].keys())}")
                database_id = db_id
                success = True
                break
            except Exception as e:
                print(f"✗ Error accessing database: {str(e)}")
                continue

        if not success:
            print("\nFailed to connect with any database ID format.")
            print("\nPlease check:")
            print("1. The database ID is correct")
            print("2. The integration has been added to the database's Share settings")
            print("3. The integration has the necessary permissions")
            print("\nDebug info:")
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
