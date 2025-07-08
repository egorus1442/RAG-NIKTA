from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import Config

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверяет API токен из заголовка Authorization"""
    if credentials.credentials != Config.API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Неверный API токен"
        )
    return credentials.credentials 