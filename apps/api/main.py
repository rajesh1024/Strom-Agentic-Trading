import os
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header, HTTPException

def get_db_path():
    return os.getenv("DB_PATH", "strom_dev.db")

def init_db():
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="STROM API Skeleton", lifespan=lifespan)

def get_current_user(x_dev_user_email: str | None = Header(None, alias="x-dev-user-email")):
    auth_mode = os.getenv("STROM_AUTH_MODE", "dev")
    if auth_mode != "dev":
        raise HTTPException(status_code=500, detail="Dev Auth Mode is disabled")
        
    if not x_dev_user_email:
        raise HTTPException(status_code=401, detail="X-Dev-User-Email header missing")

    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users WHERE email = ?", (x_dev_user_email,))
        row = cursor.fetchone()
        
        if not row:
            # Create user on first seen
            cursor.execute("INSERT INTO users (email) VALUES (?)", (x_dev_user_email,))
            conn.commit()
            user_id = cursor.lastrowid
            user_email = x_dev_user_email
        else:
            user_id, user_email = row

    return {"id": user_id, "email": user_email}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/metrics")
def metrics():
    return {"metrics": "stub"}

@app.get("/api/v1/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
