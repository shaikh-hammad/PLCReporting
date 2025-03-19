import requests
import base64, os, urllib.parse
from dotenv import load_dotenv
from datetime import datetime

current_year = str(datetime.now().year)
load_dotenv(override=True)

# Use a GitLab personal access token from your environment variables.
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
# For GitLab, the project is typically referenced as "namespace/project"
REPO_OWNER = 'plc'
REPO_NAME = 'PLCReporting'
COMMIT_MESSAGE = 'log upload'

def git_upload(FILE_NAME, FILE_PATH):
    # Read the file content and encode it in base64
    with open(FILE_PATH, 'rb') as file:
        content = base64.b64encode(file.read()).decode('utf-8')

    branch = "main"
    # GitLab expects the project path to be URL-encoded, e.g., "shaikh-hammad/PLCReporting" becomes "shaikh-hammad%2FPLCReporting"
    project = f"{REPO_OWNER}/{REPO_NAME}"
    encoded_project = urllib.parse.quote_plus(project)
    
    # Prepare the file path within the repository, then URL-encode it.
    file_path_repo = f"logs/{FILE_NAME}"
    encoded_file_path = urllib.parse.quote_plus(file_path_repo)

    # Construct the URL for the Repository Files API
    url = f"https://gitlab.com/api/v4/projects/{encoded_project}/repository/files/{encoded_file_path}?ref={branch}"

    # Use the GitLab private token for authentication
    headers = {
        'PRIVATE-TOKEN': GITLAB_TOKEN
    }

    # Check if the file already exists
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # File exists: use PUT to update
        method = requests.put
    elif response.status_code == 404:
        # File does not exist: use POST to create
        method = requests.post
    else:
        print(f'Failed to check if file exists: {response.status_code}')
        return False, "failed"

    # Payload must include branch, commit message, content and specify that content is base64 encoded.
    payload = {
        "branch": branch,
        "commit_message": COMMIT_MESSAGE,
        "content": content,
        "encoding": "base64"
    }
    
    response = method(url, json=payload, headers=headers)

    if response.status_code in (200, 201):
        print('File uploaded successfully!')
        # GitLab URL format for file view (using the "/-/blob/" path)
        return True, f"https://gitlab.com/{REPO_OWNER}/{REPO_NAME}/-/blob/{branch}/logs/{FILE_NAME}"
    else:
        print(f'Failed to upload file: {response.status_code}')
        print(response.json())
        return False, "failed"


def summarize_log_to_markdown(log_filepath, log_filename, id):
    """
    Reads a log file, counts test successes and failures, and creates a 
    markdown summary with the counts and the full log content.
    """
    md_filename = log_filename.replace(".log", ".md")
    md_filepath = f"logs/{md_filename}"
    try:
        with open(log_filepath, 'r') as log_file:
            log_content = log_file.readlines()
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_filepath}")
        return

    success_count = 0
    failure_count = 0

    for line in log_content:
        if "TEST_CASE_SUCCESS" in line:
            success_count += 1
        elif "TEST_CASE_FAILURE" in line:
            failure_count += 1

    with open(md_filepath, 'w') as md_file:
        md_file.write(f"# Test Suite Summary: {id}\n\n")
        md_file.write(f"**Total Tests:** {success_count + failure_count}\n\n")
        md_file.write(f"**Total Successes:** {success_count}\n\n")
        md_file.write(f"**Total Failures:** {failure_count}\n\n")
        md_file.write("---\n\n")
        md_file.write("## Full Log Content\n\n")
        md_file.write("```\n")
        for line in log_content:
            md_file.write(line) 
        md_file.write("```\n")

    return md_filename, md_filepath

# Example usage:
if __name__=="__main__":
    git_upload('test.log', 'test.log')
