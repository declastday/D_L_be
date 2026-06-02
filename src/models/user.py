from __future__ import annotations
from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    student_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True  # ★ 로그인 시 조회 인덱스
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    department: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True  # ★ 이메일 인증 시 조회 인덱스
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    privacy_consent = relationship(
        "PrivacyConsent", back_populates="user", uselist=False
    )
    club_memberships = relationship("ClubMember", back_populates="user")
    applications = relationship("Application", back_populates="user")
    notifications = relationship("Notification", back_populates="recipient")


class PrivacyConsent(Base):
    __tablename__ = "privacy_consents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    required_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    optional_agreed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    agreed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="privacy_consent")


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    # ★ email + is_used 복합 인덱스 추가
    # 인증번호 발송·확인 시 email + is_used 조건으로 조회하므로
    # 복합 인덱스가 단순 email 인덱스보다 훨씬 빠름
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ★ 복합 인덱스: email + is_used 조건 쿼리 최적화
    __table_args__ = (
        Index("ix_email_verifications_email_is_used", "email", "is_used"),
    )
