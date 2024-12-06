from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
# from typing import AsyncGenerator
import os, logging

app = FastAPI()
logging.basicConfig(filename="requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

async def logItem(line: str):
    logger.info(f"Request data: {line}")

@app.post("/log")
async def log(request: Request):
    body = await request.json()
    message = body.get('message')
    if message is None:
        return {"detail": "Field 'message' is required"}
    await logItem(message)
    return {"detail": "Result logged"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
