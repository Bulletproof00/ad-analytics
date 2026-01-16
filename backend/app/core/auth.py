from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .config import settings

security = HTTPBasic()


def require_basic_auth(
    credentials: HTTPBasicCredentials = Depends(security),
) -> None:
    correct_user = credentials.username == settings.basic_auth_user
    correct_pass = credentials.password == settings.basic_auth_pass
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
            headers={"WWW-Authenticate": "Basic"},
        )
