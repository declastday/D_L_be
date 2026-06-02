import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError as DBOperationalError
from sqlalchemy.orm import Session

from src.core.security import create_access_token
from src.db.session import get_db
from src.schemas.user import (
    EmailVerifySendRequest,
    EmailVerifyConfirmRequest,
    UserCreate,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from src.services import auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


# ★ 공통 DB 에러 핸들러 (기존: 모든 엔드포인트에 중복 코드 존재)
def _handle_db_error(e: DBOperationalError) -> None:
    logger.error(f"DB 연결 오류: {e}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해주세요.",
    )


@router.post(
    "/email-verify/send",
    status_code=status.HTTP_200_OK,
    summary="청주대 이메일 인증번호 발송",
)
def send_email_verification(
    body: EmailVerifySendRequest, db: Session = Depends(get_db)
):
    """청주대 이메일(@cju.ac.kr)로 6자리 인증번호 발송."""
    try:
        auth_service.send_verification_code(db, str(body.email))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DBOperationalError as e:
        _handle_db_error(e)
    except Exception as e:
        logger.error(f"이메일 발송 중 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요.",
        )
    return {"message": "인증번호가 발송되었습니다."}


@router.post(
    "/email-verify/confirm",
    status_code=status.HTTP_200_OK,
    summary="인증번호 확인",
)
def confirm_email_verification(
    body: EmailVerifyConfirmRequest, db: Session = Depends(get_db)
):
    """발송된 인증번호 유효성 확인."""
    try:
        auth_service.confirm_verification_code(db, str(body.email), body.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DBOperationalError as e:
        _handle_db_error(e)
    return {"message": "이메일 인증이 완료되었습니다."}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입 (개인정보 동의 포함)",
)
def register(body: UserCreate, db: Session = Depends(get_db)):
    """이메일 인증 완료 후 회원가입. 개인정보 수집 필수 동의 필요."""
    try:
        user = auth_service.register_user(db, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DBOperationalError as e:
        _handle_db_error(e)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인 (학번 + 비밀번호)",
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """학번 + 비밀번호 로그인 → JWT 액세스 토큰 반환.

    ★ 보안: 학번 존재 여부와 비밀번호 오류를 구분하지 않음
    → "학번 또는 비밀번호가 올바르지 않습니다" 통합 메시지
    """
    user = auth_service.authenticate_user(db, body.student_id, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="학번 또는 비밀번호가 올바르지 않습니다.",
            # ★ WWW-Authenticate 헤더 추가 (OAuth2 표준 준수)
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token)
