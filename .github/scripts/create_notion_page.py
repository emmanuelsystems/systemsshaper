import os
import subprocess
from datetime import datetime
from notion_client import Client
from openai import OpenAI

def get_commit_info():
    """Get the latest commit information"""
    commit_msg = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()
    commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    author = subprocess.check_output(['git', 'log', '-1', '--pretty=%an']).decode('utf-8').strip()
    date = subprocess.check_output(['git', 'log', '-1', '--pretty=%aI']).decode('utf-8').strip()
    
    # Get list of changed files
    changed_files = subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD']).decode('utf-8').strip().split('\n')
    
    return {
        'message': commit_msg,
        'hash': commit_hash,
        'author': author,
        'date': date,
        'changed_files': changed_files
    }

def generate_content_with_gpt(commit_info):
    """Generate a detailed description using GPT"""
    openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""Analyze this git commit and create a detailed, well-structured summary:

Commit Message: {commit_info['message']}
Author: {commit_info['author']}
Changed Files: {', '.join(commit_info['changed_files'])}

Please include:
1. Main changes and their purpose
2. Technical impact
3. Any notable implementation details
"""

    completion = openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a technical writer who creates clear, concise summaries of code changes."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return completion.choices[0].message.content

def create_notion_page(commit_info, gpt_summary):
    """Create a new page in Notion with commit information"""
    notion = Client(auth=os.getenv('NOTION_API_KEY'))
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    # Create the page
    new_page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": f"Commit: {commit_info['message'][:50]}..."
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": commit_info['date']
                }
            }
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Commit Information"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": f"Hash: {commit_info['hash']}\nAuthor: {commit_info['author']}\nDate: {commit_info['date']}"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Changed Files"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"text": {"content": "\n".join(commit_info['changed_files'])}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "GPT Analysis"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": gpt_summary}}]
                }
            }
        ]
    )
    
    return new_page.id

def main():
    try:
        # Get commit information
        commit_info = get_commit_info()
        
        # Generate content summary using GPT
        gpt_summary = generate_content_with_gpt(commit_info)
        
        # Create Notion page
        page_id = create_notion_page(commit_info, gpt_summary)
        
        print(f"Successfully created Notion page: {page_id}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
