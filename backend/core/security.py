import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import get_settings
from core.utils import encoding_base64_string

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")








# def get_access_from_refresh_token(db, refresh_token: str):
#     payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#     token_data = schemas.RefreshTokenPayload(**payload)
#     token_user = db.query(models.User).filter(models.User.email == token_data.email).first()
#     try:
#         meta = dict(token_user.meta)
#         version = meta['version']
#     except:
#         version = None
#     if not version == payload.get('version'):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )
#     return token_user


# async def create_login_token(user: models.User, refresh_token: str):
#     try:
#         meta = dict(user.meta)
#         version = meta['version']
#     except:
#         version = None
#     access_token, exp = await create_access_token(None, user=user)
#     ref_token = await create_refresh_token(None, user=user)
#     return {
#         "access_token": access_token,
#         "refresh_token": ref_token,
#         "expiry_time": exp
#     }


def encoding_token(token_data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=get_settings().access_token_expire_minutes)
    token_data.update({"exp": expire, 'token_type': 'access'})
    encoded_jwt = jwt.encode(token_data, get_settings().jwt_secret_key, algorithm=get_settings().jwt_algorithm)
    print("token: ", encoding_base64_string(str(encoded_jwt)))
    return encoding_base64_string(str(encoded_jwt))
