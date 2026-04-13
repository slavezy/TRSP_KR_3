import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Task 6.1 - Basic Auth")
security = HTTPBasic()

# In-memory "database"
fake_users = {
    "admin": "secret",
    "user1": "password1",
}


@app.get("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    stored_password = fake_users.get(credentials.username)

    # Use secrets.compare_digest to prevent timing attacks
    password_correct = stored_password is not None and secrets.compare_digest(
        credentials.password.encode(), stored_password.encode()
    )

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return {"message": "You got my secret, welcome"}
