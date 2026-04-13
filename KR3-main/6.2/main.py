import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="Task 6.2 - Password Hashing")
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory database
fake_users_db: dict = {}


# ---------- Pydantic models ----------

class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


# ---------- Dependencies ----------

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    user: UserInDB | None = fake_users_db.get(credentials.username)

    # Compare usernames in constant time
    username_correct = user is not None and secrets.compare_digest(
        credentials.username.encode(), user.username.encode()
    )
    # Verify hashed password (bcrypt already resists timing attacks, but we
    # only call verify when the username matched to avoid leaking existence)
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


# ---------- Endpoints ----------

@app.post("/register", status_code=201)
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(
        username=user.username, hashed_password=hashed
    )
    return {"message": f"User '{user.username}' successfully registered"}


@app.get("/login")
def login(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {current_user.username}!"}
