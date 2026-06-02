import json
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── DB ──────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── 앱 환경 ─────────────────────────────────────────────────
    ENVIRONMENT: str = "production"   # ★ 기본값 변경: 배포 환경을 production으로
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # ── 인증 ─────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Supabase ─────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── 이메일 (Resend) ──────────────────────────────────────────
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@dreamlounge.site"  # ★ 실제 도메인으로 변경

    # ── CORS ─────────────────────────────────────────────────────
    # 로컬: '["http://localhost:3000"]'
    # 배포: '["https://dreamlounge.site","https://www.dreamlounge.site"]'
    FRONTEND_URL: str = "https://dreamlounge.site"       # ★ 배포 도메인으로 변경
    ALLOWED_ORIGINS: str = '["https://dreamlounge.site","https://www.dreamlounge.site"]'  # ★

    # ── 이메일 인증 ──────────────────────────────────────────────
    EMAIL_VERIFICATION_EXPIRY_MINUTES: int = 30
    CJU_EMAIL_DOMAIN: str = "cju.ac.kr"

    # ── DB 커넥션 풀 (★ 추가: 성능 핵심) ──────────────────────────
    DB_POOL_SIZE: int = 10          # 동시에 유지할 연결 수
    DB_MAX_OVERFLOW: int = 20       # 풀 초과 시 추가로 허용할 연결 수
    DB_POOL_TIMEOUT: int = 30       # 연결 대기 최대 시간(초)
    DB_POOL_RECYCLE: int = 1800     # 30분마다 연결 재생성 (DB 끊김 방지)

    def get_allowed_origins(self) -> List[str]:
        return json.loads(self.ALLOWED_ORIGINS)

    model_config = {"env_file": ".env", "extra": "ignore"}


# ★ lru_cache: Settings 객체를 한 번만 생성해 재사용 (매 요청마다 .env 재파싱 방지)
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
