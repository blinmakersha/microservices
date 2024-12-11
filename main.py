import enum
import time
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter("app_requests_total", "Total number of requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])

class Job(enum.Enum):
    LOWER = 'lower'
    UPPER = 'upper'

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    JOB: Job = Job.LOWER

settings = Settings()

app = FastAPI()

JOB_TO_FUNCTION = {
    Job.LOWER: lambda x: x.lower(),
    Job.UPPER: lambda x: x.upper()
}

class DoRequest(BaseModel):
    message: str

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()

        response = await call_next(request)

        request_latency = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(request_latency)

        return response

app.add_middleware(MetricsMiddleware)

@app.post("/api/v1/process_request")
async def process_request(body: DoRequest):
    func = JOB_TO_FUNCTION[settings.JOB]
    return {"result": func(body.message)}

@app.get("/get_metrics")
async def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)