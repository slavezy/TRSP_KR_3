import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ---------- Config ----------

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------- App + rate limiter ----------

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Task 6.5 - JWT + Registration + Rate Limit")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict = {}  # username -> {"username": str, "hashed_password": str}


# ---------- Schemas ----------

class UserRequest(BaseModel):
    username: str
    password: str


# ---------- Helpers ----------

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------- Endpoints ----------

@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register(request: Request, data: UserRequest):
    # Check existence using secrets.compare_digest to avoid timing attacks
    for existing in fake_users_db:
        if secrets.compare_digest(existing, data.username):
            raise HTTPException(status_code=409, detail="User already exists")

    fake_users_db[data.username] = {
        "username": data.username,
        "hashed_password": pwd_context.hash(data.password),
    }
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, data: UserRequest):
    # Find user in constant time
    user = None
    for existing, user_data in fake_users_db.items():
        if secrets.compare_digest(existing, data.username):
            user = user_data
            break

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")

    token = create_access_token({"sub": data.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(payload: dict = Depends(verify_token)):
    return {"message": "Access granted", "user": payload.get("sub")}
