from datetime import datetime, timedelta, timezone
from functools import lru_cache
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.config import settings

# ★ CryptContext 전역 1회 생성 (기존과 동일, 위치만 명확히)
# 매 요청마다 새로 만들면 bcrypt 초기화 비용 발생
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """입력 비밀번호와 해시값 비교."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """JWT 액세스 토큰 생성."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expire
    # ★ sub는 반드시 str 타입으로 변환 (UUID 직렬화 오류 방지)
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """JWT 토큰 디코딩. 만료·서명 오류 시 JWTError 발생."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
