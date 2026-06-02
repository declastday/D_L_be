from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from src.core.config import settings

# ★ 커넥션 풀 설정 추가 (성능 핵심)
# 기존: create_engine(DATABASE_URL) → 요청마다 새 연결 생성 → 느림
# 변경: 풀에서 연결 재사용 → 연결 생성 비용 제거 → 빠름
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,         # 기본 유지 연결 수 (10)
    max_overflow=settings.DB_MAX_OVERFLOW,   # 풀 초과 시 추가 연결 (20) → 최대 30개
    pool_timeout=settings.DB_POOL_TIMEOUT,   # 연결 대기 최대 30초
    pool_recycle=settings.DB_POOL_RECYCLE,   # 30분마다 연결 갱신 (Supabase 끊김 방지)
    pool_pre_ping=True,                      # ★ 연결 사용 전 유효성 체크 (끊긴 연결 자동 교체)
    echo=settings.DEBUG,                     # DEBUG=True 일 때만 SQL 로그 출력
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 DB 세션 제공."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
