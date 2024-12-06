from fastapi import FastAPI, Request
from datetime import datetime
from fastapi.responses import StreamingResponse
import gitupload
# from typing import AsyncGenerator
import os, logging, git

app = FastAPI()
logging.basicConfig(filename="requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)
repo = git.Repo('.', search_parent_directories=True)
repo_path = repo.working_tree_dir

async def logItem(line: str, id, eof):
    # logger = logging.getLogger('my_logger')
    # logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    filename = f"{id}_{datetime.now().strftime('%Y%m%d')}.log"
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f"Request data: {line}")

    if eof:
        gitupload.git_upload(filename, filename)

@app.post("/log")
async def log(request: Request):
    body = await request.json()
    message = body.get('message')
    id = body.get("id")
    eof = bool(body.get("eof"))
    if message is None or id is None or eof is None:
        return {"detail": "Fields 'message, id, eof' are required"}
    await logItem(message, id, eof)
    return {"detail": "Result logged"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
