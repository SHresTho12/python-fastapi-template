import http
import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError
from core.config import get_config
config = get_config()

class TokenVerifier:
    def __init__(self, token_type: str):
        self.token_type = token_type
        self.jwt_algorithm = config.jwt_algorithm

    def verify_hashed_token(self, expected_token: str, credentials: HTTPAuthorizationCredentials):
        if credentials.credentials != expected_token:
            raise HTTPException(
                status_code=403,
                detail=f"Invalid or missing {self.token_type} token"
            )

    def verify_jwt_token(self, secret_key: str, token: str = None, credentials: HTTPAuthorizationCredentials = None):
        jwt_token = token if token else credentials.credentials if credentials else None
        if not jwt_token:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail=f"Missing {self.token_type}"
            )

        # Decode and verify the JWT token
        try:
            payload = jwt.decode(jwt_token, secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except PyJWTError as e:
            print(f"{self.token_type.capitalize()} token verification error:", e)
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail=f"Invalid or expired {self.token_type}"
            )


# Instantiate verifiers for different token types
api_token_verifier = TokenVerifier(token_type="api")
admin_token_verifier = TokenVerifier(token_type="admin")
access_token_verifier = TokenVerifier(token_type="access token")
refresh_token_verifier = TokenVerifier(token_type="refresh token")


def verify_api_token(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    api_token_verifier.verify_hashed_token(config.api_key, credentials)

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    admin_token_verifier.verify_hashed_token(config.admin_auth, credentials)

def verify_access_token(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    return access_token_verifier.verify_jwt_token(config.access_token_secret_key, credentials=credentials)

def verify_refresh_token(token: str):
    return refresh_token_verifier.verify_jwt_token(config.refresh_token_secret_key, token=token)
