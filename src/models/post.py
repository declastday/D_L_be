from __future__ import annotations
from uuid import uuid4
from sqlalchemy import String, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base, TimestampMixin


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    # ★ club_id 인덱스 추가 (동아리 게시판 조회 시 사용)
    club_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clubs.id"), nullable=False, index=True
    )
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    post_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="general"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_notice: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # ★ is_deleted 소프트 삭제 — DB에서 완전 삭제하지 않고 숨김 처리
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    club = relationship("Club", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )

    # ★ 복합 인덱스: 동아리 게시판 조회 최적화
    # club_id + is_deleted=False 조건 쿼리에 사용
    __table_args__ = (
        Index("ix_posts_club_id_is_deleted", "club_id", "is_deleted"),
    )


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    # ★ post_id 인덱스 추가 (게시글 댓글 조회 시 사용)
    post_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("posts.id"), nullable=False, index=True
    )
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    post = relationship("Post", back_populates="comments")
