from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.core.security import decode_access_token

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    """JWT 토큰 검증 후 현재 사용자 반환.

    ★ 변경: 에러 메시지 통일
    기존: 토큰 오류 / 사용자 없음 두 가지 메시지 분리
    변경: 동일한 메시지로 통일 → 공격자가 토큰 유효성 여부 파악 불가
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증이 필요합니다. 다시 로그인해주세요.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # ★ 순환 import 방지: 함수 내부에서 import (기존 코드와 동일 패턴 유지)
    from src.models.user import User

    # ★ db.get() 사용 (기존과 동일 — PK 조회라 가장 빠름)
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return user
