import requests
import base64

GITHUB_TOKEN = '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'
REPO_OWNER = 'shaikh-hammad'
REPO_NAME = 'PLCReporting'
COMMIT_MESSAGE = 'log upload'

def git_upload(FILE_NAME):
    # Read the file content and encode it in base64
    with open(FILE_NAME, 'rb') as file:
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
    else:
        print(f'Failed to upload file: {response.status_code}')
        print(response.json())

# if __name__=="__main__":
#     git_upload('test.log', 'test.log')