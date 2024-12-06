from fastapi import FastAPI, Request
from datetime import datetime
from fastapi.responses import StreamingResponse
# from typing import AsyncGenerator
import os, logging

app = FastAPI()
logging.basicConfig(filename="requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

async def logItem(line: str, id):
    # logger = logging.getLogger('my_logger')
    # logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    handler = logging.FileHandler(f"{id}_{datetime.now().strftime('%Y%m%d')}.log")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f"Request data: {line}")

@app.post("/log")
async def log(request: Request):
    body = await request.json()
    message = body.get('message')
    id = body.get("id")
    eof = body.get("EOF")
    if message is None:
        return {"detail": "Field 'message' is required"}
    await logItem(message, id)
    return {"detail": "Result logged"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
