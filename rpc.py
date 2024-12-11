import httpx
import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rpc")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    UPPER_URL: str = 'http://upper:8000/api/v1/process_request'
    LOWER_URL: str = 'http://lower:8000/api/v1/process_request'


settings = Settings()


SERVER_METHOD = {
    'message.upper': settings.UPPER_URL,
    'message.lower': settings.LOWER_URL,
}


@app.post("/rpc")
async def handle_rpc(request: Request):
    logger.info("Received RPC request")
    rpc_request = await request.json()

    method = rpc_request.get("method")
    data = rpc_request.get("data")

    url = SERVER_METHOD.get(method)

    if not url:
        raise HTTPException(detail={"error": "NOT_FOUND"}, status_code=status.HTTP_404_NOT_FOUND)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
    return JSONResponse(content=response.json(), status_code=response.status_code)
