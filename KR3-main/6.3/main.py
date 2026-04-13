import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "secret")

if MODE not in ("DEV", "PROD"):
    raise ValueError(f"Invalid MODE='{MODE}'. Allowed values: DEV, PROD")

# Disable all built-in doc routes — we override them manually below
app = FastAPI(
    title="Task 6.3 - Docs Auth",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_users_db: dict = {}


# ---------- Docs auth dependency ----------

def verify_docs_creds(credentials: HTTPBasicCredentials = Depends(security)):
    user_ok = secrets.compare_digest(
        credentials.username.encode(), DOCS_USER.encode()
    )
    pass_ok = secrets.compare_digest(
        credentials.password.encode(), DOCS_PASSWORD.encode()
    )
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


# ---------- Docs routes ----------

if MODE == "DEV":

    @app.get("/docs", include_in_schema=False)
    def docs(_: HTTPBasicCredentials = Depends(verify_docs_creds)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

    @app.get("/openapi.json", include_in_schema=False)
    def openapi(_: HTTPBasicCredentials = Depends(verify_docs_creds)):
        return get_openapi(title=app.title, version=app.version, routes=app.routes)

    # /redoc is hidden in DEV too (as per task)

else:  # PROD

    @app.get("/docs", include_in_schema=False)
    def docs_prod():
        raise HTTPException(status_code=404)

    @app.get("/openapi.json", include_in_schema=False)
    def openapi_prod():
        raise HTTPException(status_code=404)

    @app.get("/redoc", include_in_schema=False)
    def redoc_prod():
        raise HTTPException(status_code=404)


# ---------- Business logic (reused from task 6.2) ----------

class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    user: UserInDB | None = fake_users_db.get(credentials.username)
    username_correct = user is not None and secrets.compare_digest(
        credentials.username.encode(), user.username.encode()
    )
    password_correct = username_correct and pwd_context.verify(
        credentials.password, user.hashed_password
    )
    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@app.post("/register", status_code=201)
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    fake_users_db[user.username] = UserInDB(
        username=user.username, hashed_password=pwd_context.hash(user.password)
    )
    return {"message": f"User '{user.username}' successfully registered"}


@app.get("/login")
def login(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {current_user.username}!"}
