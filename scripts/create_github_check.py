import requests
import json
import os

def create_github_check(metadata_deletions):
    repo = os.getenv('GITHUB_REPOSITORY')
    sha = os.getenv('GITHUB_SHA')
    app_id = os.getenv('GITHUB_APP_ID')
    app_key = os.getenv('GITHUB_APP_KEY')

    url = f"https://api.github.com/repos/{repo}/check-runs"
    headers = {
        "Authorization": f"Bearer {app_key}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": "Package Metadata Deletions",
        "head_sha": sha,
        "status": "completed",
        "conclusion": "neutral",
        "output": {
            "title": "Metadata Deletions",
            "summary": "The following metadata deletions were found:",
            "text": json.dumps(metadata_deletions, indent=2)
        }
    }

    if metadata_deletions:
        data["conclusion"] = "action_required"

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

if __name__ == "__main__":
    with open('metadata_deletions.json') as f:
        metadata_deletions = json.load(f)
    create_github_check(metadata_deletions)
