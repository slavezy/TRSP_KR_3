from fastapi import FastAPI
from pydantic import BaseModel

from database import create_tables, get_db_connection

app = FastAPI(title="Task 8.1 - SQLite Registration")

# Create table on startup
create_tables()


class User(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(user: User):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, user.password),
    )
    conn.commit()
    conn.close()
    return {"message": "User registered successfully!"}
