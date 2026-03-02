FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install fastapi uvicorn
WORKDIR /app
COPY main.py .
EXPOSE 8001
CMD ["python", "main.py"]
