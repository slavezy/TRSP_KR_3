from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel

# ---------- Config ----------

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------- RBAC setup ----------

ROLES_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["create", "read", "update", "delete"],
    "user": ["read", "update"],
    "guest": ["read"],
}

# ---------- App ----------

app = FastAPI(title="Task 7.1 - RBAC")
bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pre-seeded users for testing
fake_users_db: dict = {
    "admin_user": {
        "username": "admin_user",
        "hashed_password": pwd_context.hash("adminpass"),
        "role": "admin",
    },
    "regular_user": {
        "username": "regular_user",
        "hashed_password": pwd_context.hash("userpass"),
        "role": "user",
    },
    "guest_user": {
        "username": "guest_user",
        "hashed_password": pwd_context.hash("guestpass"),
        "role": "guest",
    },
}


# ---------- Schemas ----------

class UserRequest(BaseModel):
    username: str
    password: str
    role: str = "guest"


# ---------- Helpers ----------

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return {"username": payload["sub"], "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_permission(permission: str):
    """Dependency factory: checks that the current user has a specific permission."""
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if permission not in ROLES_PERMISSIONS.get(user["role"], []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: '{permission}'",
            )
        return user
    return checker


# ---------- Auth endpoints ----------

@app.post("/register", status_code=201)
def register(data: UserRequest):
    if data.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    if data.role not in ROLES_PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {list(ROLES_PERMISSIONS)}")

    fake_users_db[data.username] = {
        "username": data.username,
        "hashed_password": pwd_context.hash(data.password),
        "role": data.role,
    }
    return {"message": f"User '{data.username}' registered with role '{data.role}'"}


@app.post("/login")
def login(data: UserRequest):
    user = fake_users_db.get(data.username)
    if not user or not pwd_context.verify(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": data.username, "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}


# ---------- Protected endpoints ----------

@app.get("/protected_resource")
def protected_resource(user: dict = Depends(get_current_user)):
    return {"message": f"Access granted to '{user['username']}' (role: {user['role']})"}


@app.post("/resources")
def create_resource(user: dict = Depends(require_permission("create"))):
    return {"message": f"Resource created by '{user['username']}' (admin only)"}


@app.get("/resources")
def read_resources(user: dict = Depends(require_permission("read"))):
    return {"message": f"Resources listed for '{user['username']}'"}


@app.put("/resources/{resource_id}")
def update_resource(resource_id: int, user: dict = Depends(require_permission("update"))):
    return {"message": f"Resource {resource_id} updated by '{user['username']}'"}


@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, user: dict = Depends(require_permission("delete"))):
    return {"message": f"Resource {resource_id} deleted by '{user['username']}' (admin only)"}
