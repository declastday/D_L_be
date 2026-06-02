import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schemas.club import ClubResponse, ApplicationFormResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.get(
    "/{club_id}",
    response_model=ClubResponse,
    summary="동아리 상세 조회 (비회원 포함)",
)
def get_club(club_id: str, db: Session = Depends(get_db)):
    """동아리 상세 정보 조회. 로그인 없이 접근 가능."""
    # TODO: club_service.get_club(db, club_id) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )


@router.get(
    "/{club_id}/form",
    response_model=ApplicationFormResponse,
    summary="동아리 신청 폼(질문 목록) 조회",
)
def get_club_form(club_id: str, db: Session = Depends(get_db)):
    """해당 동아리의 활성화된 신청 폼과 질문 목록 조회."""
    # TODO: application_service.get_active_form(db, club_id) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )
