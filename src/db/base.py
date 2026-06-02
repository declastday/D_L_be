from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    """★ timezone-aware UTC 현재 시각 반환.

    기존: datetime.utcnow() → timezone 정보 없음 (naive datetime)
         Python 3.12+ 에서 deprecation warning 발생
    변경: datetime.now(timezone.utc) → timezone-aware datetime
    """
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """생성·수정 시각을 자동으로 기록하는 믹스인.

    ★ 변경: datetime.utcnow → _utcnow() (timezone-aware)
    모든 모델에서 공통으로 사용하므로 여기서만 수정하면 전체 적용
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),   # ★ timezone=True 추가
        default=_utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),   # ★ timezone=True 추가
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
