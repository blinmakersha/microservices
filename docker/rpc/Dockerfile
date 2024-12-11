FROM python:3.12-slim
WORKDIR /app
RUN pip install "fastapi[standard]" httpx pydantic-settings
COPY rpc.py /app/main.py

