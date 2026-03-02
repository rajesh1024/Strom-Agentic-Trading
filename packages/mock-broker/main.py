from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Mock Broker API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
