import requests
import base64, re

GITHUB_TOKEN = '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'
REPO_OWNER = 'shaikh-hammad'
REPO_NAME = 'PLCReporting'
COMMIT_MESSAGE = 'log upload'

def git_upload(FILE_NAME, FILE_PATH):
    # Read the file content and encode it in base64
    with open(FILE_PATH, 'rb') as file:
        content = base64.b64encode(file.read()).decode('utf-8')

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/logs/{FILE_NAME}'

    payload = {
        'message': COMMIT_MESSAGE,
        'content': content
    }

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.put(url, json=payload, headers=headers)

    if response.status_code == 201:
        print('File uploaded successfully!')
        return True, f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/logs/{FILE_NAME}"
    else:
        print(f'Failed to upload file: {response.status_code}')
        print(response.json())
        return False, "failed"

def summarize_log_to_markdown(log_filepath, log_filename):
    """
    Reads a log file, counts test successes and failures, and creates a 
    markdown summary with the counts and the full log content.

    Args:
        log_filepath: Path to the input log file.
        markdown_filepath: Path to the output markdown file.
    """
    md_filename = log_filename.replace(".log", ".md")
    md_filepath = f"local_logs/{md_filename}"
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
        md_file.write("# Test Suite Summary\n\n")
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

# if __name__=="__main__":
#     git_upload('test.log')