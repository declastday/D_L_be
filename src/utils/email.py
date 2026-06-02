import logging
import resend
from src.core.config import settings

logger = logging.getLogger(__name__)

# ★ api_key를 모듈 로드 시 1회만 설정
# 기존: 모듈 로드 시 설정하지만 send 함수마다 키 유무 체크
resend.api_key = settings.RESEND_API_KEY

# ★ 이메일 HTML 템플릿 상수화
# 기존: 함수 호출마다 문자열 조합 → 작은 비용이지만 반복 시 낭비
_VERIFICATION_HTML = """
<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px">
  <h2 style="color:#4F46E5">Dream Lounge</h2>
  <p>안녕하세요!<br>이메일 인증번호를 알려드립니다.</p>
  <div style="background:#F3F4F6;border-radius:8px;padding:24px;text-align:center;margin:24px 0">
    <span style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#1F2937">{code}</span>
  </div>
  <p style="color:#6B7280;font-size:14px">
    인증번호는 <strong>{expires_minutes}분</strong> 동안 유효합니다.<br>
    본인이 요청하지 않은 경우 이 메일을 무시해주세요.
  </p>
</div>
"""

_APPLICATION_RESULT_HTML = """
<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px">
  <h2 style="color:#4F46E5">Dream Lounge</h2>
  <p>안녕하세요!<br><strong>{club_name}</strong> 동아리 신청 결과를 알려드립니다.</p>
  <div style="background:#F3F4F6;border-radius:8px;padding:24px;text-align:center;margin:24px 0">
    <span style="font-size:24px;font-weight:bold;color:{status_color}">{status_text}</span>
  </div>
  <p style="color:#6B7280;font-size:14px">
    자세한 내용은 Dream Lounge에서 확인해주세요.
  </p>
</div>
"""

# ★ 상태별 텍스트·색상 매핑 상수화
_STATUS_MAP = {
    "pending": ("보류 (1차 합격)", "#F59E0B"),
    "passed":  ("최종 합격 🎉",    "#10B981"),
    "failed":  ("불합격",          "#EF4444"),
}


def send_verification_email(to_email: str, code: str) -> None:
    """6자리 인증번호가 포함된 이메일 발송."""
    # ★ API 키 체크를 함수 진입 시 즉시 수행 (기존과 동일하지만 명시적)
    if not settings.RESEND_API_KEY:
        logger.error("RESEND_API_KEY가 설정되지 않았습니다.")
        raise RuntimeError("이메일 서비스 API 키가 설정되지 않았습니다.")

    try:
        result = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "[Dream Lounge] 이메일 인증번호",
            "html": _VERIFICATION_HTML.format(
                code=code,
                expires_minutes=settings.EMAIL_VERIFICATION_EXPIRY_MINUTES,
            ),
        })
        logger.info(f"인증번호 이메일 발송 성공: to={to_email}, id={result.id}")
    except Exception as e:
        logger.error(f"이메일 발송 실패: to={to_email}, error={e}", exc_info=True)
        raise


def send_application_result_email(
    to_email: str, club_name: str, result_status: str
) -> None:
    """신청서 심사 결과(passed/pending/failed) 이메일 발송.

    ★ 기존: NotImplementedError → 구현 완료
    신청서 상태 변경 시 해당 학생에게 결과 이메일 발송
    """
    if not settings.RESEND_API_KEY:
        logger.error("RESEND_API_KEY가 설정되지 않았습니다.")
        raise RuntimeError("이메일 서비스 API 키가 설정되지 않았습니다.")

    status_text, status_color = _STATUS_MAP.get(
        result_status, ("결과 확인", "#6B7280")
    )

    try:
        result = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": f"[Dream Lounge] {club_name} 신청 결과 안내",
            "html": _APPLICATION_RESULT_HTML.format(
                club_name=club_name,
                status_text=status_text,
                status_color=status_color,
            ),
        })
        logger.info(
            f"신청 결과 이메일 발송 성공: to={to_email}, "
            f"club={club_name}, status={result_status}, id={result.id}"
        )
    except Exception as e:
        logger.error(
            f"신청 결과 이메일 발송 실패: to={to_email}, error={e}", exc_info=True
        )
        raise
