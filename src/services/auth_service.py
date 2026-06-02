import random
import string
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import hash_password, verify_password
from src.models.user import User, PrivacyConsent, EmailVerification
from src.schemas.user import UserCreate
from src.utils.email import send_verification_email

logger = logging.getLogger(__name__)

# ★ 인증번호 길이 상수화 (기존: 코드에 6 하드코딩)
_CODE_LENGTH = 6


def _generate_code() -> str:
    """6자리 랜덤 숫자 인증번호 생성."""
    return "".join(random.choices(string.digits, k=_CODE_LENGTH))


def _get_valid_verification(
    db: Session, email: str, code: str
) -> EmailVerification | None:
    """미사용·미만료 레코드 중 코드가 일치하는 것을 반환."""
    return (
        db.query(EmailVerification)
        .filter(
            EmailVerification.email == email,
            EmailVerification.code == code,
            EmailVerification.is_used == False,
            EmailVerification.expires_at > datetime.utcnow(),
        )
        .first()
    )


def send_verification_code(db: Session, email: str) -> None:
    """청주대 이메일로 6자리 인증번호 발송. 이전 대기 레코드는 모두 만료 처리."""
    # ★ 이메일 도메인 검증
    if not email.lower().endswith(f"@{settings.CJU_EMAIL_DOMAIN}"):
        raise ValueError(
            f"청주대학교 이메일(@{settings.CJU_EMAIL_DOMAIN})만 사용할 수 있습니다."
        )

    code = _generate_code()

    # ★ 기존 미사용 인증번호 일괄 만료 처리 (재발송 시 이전 코드 무효화)
    db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.is_used == False,
    ).update({"is_used": True})

    db.add(
        EmailVerification(
            email=email,
            code=code,
            is_used=False,
            expires_at=datetime.utcnow()
            + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRY_MINUTES),
        )
    )
    db.commit()

    # ★ 이메일 발송은 DB 커밋 후 (커밋 실패 시 이메일 발송 방지)
    send_verification_email(email, code)
    logger.info(f"인증번호 발송 완료: {email}")


def confirm_verification_code(db: Session, email: str, code: str) -> None:
    """인증번호 유효성 확인 (UX 피드백용). 상태를 변경하지 않는다."""
    if not _get_valid_verification(db, email, code):
        raise ValueError("인증번호가 올바르지 않거나 만료되었습니다.")


def register_user(db: Session, data: UserCreate) -> User:
    """인증번호 검증 → 중복 검사 → User + PrivacyConsent 생성."""
    email = str(data.email)

    # ① 인증번호 검증
    verification = _get_valid_verification(db, email, data.verification_code)
    if not verification:
        raise ValueError(
            "이메일 인증번호가 올바르지 않거나 만료되었습니다. 인증번호를 다시 요청해주세요."
        )

    # ② 필수 개인정보 동의 확인
    if not data.privacy_consent.required_agreed:
        raise ValueError("필수 개인정보 수집 동의가 필요합니다.")

    # ③ 중복 확인 (★ 학번·이메일 동시 조회로 DB 쿼리 1회 절약)
    existing = (
        db.query(User)
        .filter(
            (User.student_id == data.student_id) | (User.email == email)
        )
        .first()
    )
    if existing:
        if existing.student_id == data.student_id:
            raise ValueError("이미 가입된 학번입니다.")
        raise ValueError("이미 가입된 이메일입니다.")

    # ④ 비밀번호 강도 검증 (★ 추가: 보안)
    _validate_password_strength(data.password)

    # ⑤ User 생성
    user = User(
        student_id=data.student_id,
        password_hash=hash_password(data.password),
        name=data.name,
        phone=data.phone,
        department=data.department,
        email=email,
        email_verified=True,
    )
    db.add(user)
    db.flush()  # user.id 확보 (커밋 없이)

    # ⑥ 개인정보 동의 기록
    db.add(
        PrivacyConsent(
            user_id=user.id,
            required_agreed=data.privacy_consent.required_agreed,
            optional_agreed=data.privacy_consent.optional_agreed,
        )
    )

    # ⑦ 인증번호 사용 처리
    verification.is_used = True
    db.commit()
    db.refresh(user)

    logger.info(f"회원가입 완료: {email}")
    return user


def authenticate_user(db: Session, student_id: str, password: str) -> User | None:
    """학번 + 비밀번호 검증. 성공 시 User 반환, 실패 시 None.

    ★ 보안: 학번 존재 여부와 비밀번호 오류를 구분하지 않음
    → 공격자가 유효한 학번을 알아낼 수 없도록 방지
    """
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        # ★ 타이밍 공격 방지: 학번이 없어도 해싱 시간만큼 지연
        hash_password("dummy_to_prevent_timing_attack")
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def _validate_password_strength(password: str) -> None:
    """비밀번호 강도 검증. (★ 추가)
    - 최소 8자
    - 영문·숫자 포함
    """
    if len(password) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 합니다.")
    has_alpha = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_alpha and has_digit):
        raise ValueError("비밀번호는 영문과 숫자를 모두 포함해야 합니다.")
