from fastapi import FastAPI, Request
from datetime import datetime
from fastapi.responses import StreamingResponse
import gitupload
# from typing import AsyncGenerator
import os, logging

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

async def logItem(line: str, test_name,id, eof, test_status):
    # logger = logging.getLogger('my_logger')
    # logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    id = id.replace(' ', '_')
    filename = f"{id}_{datetime.now().strftime('%Y%m%d')}.log"
    filepath = f"local_logs/{filename}"
    handler = logging.FileHandler(filepath)
    handler.setLevel(logging.DEBUG)
    if int(test_status) == 1:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(test_name)s - TEST_CASE_SUCCESS - %(message)s')
    elif int(test_status) == 0:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(test_name)s - TEST_CASE_FAILURE - %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(f"Request data: {line}", extra={"test_name": test_name})
    if eof == 'True':
        md_filename, md_filepath = gitupload.summarize_log_to_markdown(filepath, filename, id)
        result, url = gitupload.git_upload(md_filename, md_filepath)
        if result is True:
            try:
                for handler in logger.handlers[:]:
                    logger.removeHandler(handler)
                    handler.close()
                os.remove(filepath)
                os.remove(md_filepath)
                print('Local log file deleted successfully!')
            except Exception as e:
                print(f'Failed to delete local file: {e}')
            return result, url
    return True, "logged"


@app.post("/log")
async def log(request: Request):
    body = await request.json()
    message = body.get('message')
    id = body.get("id")
    test_name = body.get('test_name')
    eof = body.get("eof")
    test_status = body.get("test_status")
    if message is None or id is None or eof is None or test_name is None:
        return {"detail": "Fields 'message, id, eof' are required"}
    result, url = await logItem(message, test_name, id, eof, test_status) 
    if result == False:
        return {"detail": "Result failed to log."}
    return {"detail": "Result logged successfully!", "url": url}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
