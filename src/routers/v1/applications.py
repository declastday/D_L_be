import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.core.dependencies import get_current_user
from src.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListItem,
)

logger = logging.getLogger(__name__)

# ★ prefix를 /me로 분리 (기존: prefix 없어서 경로 충돌 가능)
# /applications → 신청서 생성·수정
# /me/applications → 내 신청서 조회
router = APIRouter(tags=["applications"])


@router.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="신청서 임시저장 또는 제출",
)
def create_application(
    body: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """is_draft=true: 임시저장 / is_draft=false: 최종 제출."""
    # TODO: application_service.create_application(db, body, current_user) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )


@router.patch(
    "/applications/{application_id}",
    response_model=ApplicationResponse,
    summary="임시저장 신청서 수정 또는 최종 제출",
)
def update_application(
    application_id: str,
    body: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """임시저장 신청서 수정. is_draft=false로 변경하면 최종 제출."""
    # TODO: application_service.update_application(db, application_id, body, current_user) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )


# ── 마이페이지 - 임시저장함 ─────────────────────────────────────────


@router.get(
    "/me/applications/drafts",
    response_model=list[ApplicationListItem],
    summary="임시저장함 목록 조회",
)
def get_draft_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 임시저장한 신청서 목록."""
    # TODO: application_service.get_drafts(db, current_user.id) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )


@router.get(
    "/me/applications/drafts/{application_id}",
    response_model=ApplicationResponse,
    summary="임시저장 신청서 상세 조회 (수정 가능)",
)
def get_draft_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """임시저장 신청서 상세. 수정 후 저장 또는 제출 가능."""
    # TODO: application_service.get_draft(db, application_id, current_user.id) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )


# ── 마이페이지 - 나의 신청서 ────────────────────────────────────────


@router.get(
    "/me/applications/submitted",
    response_model=list[ApplicationListItem],
    summary="제출한 신청서 목록 (상태 포함)",
)
def get_submitted_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """제출한 신청서 목록. 각 항목에 현재 상태(대기/보류/합격/불합격) 포함."""
    # TODO: application_service.get_submitted(db, current_user.id) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )


@router.get(
    "/me/applications/submitted/{application_id}",
    response_model=ApplicationResponse,
    summary="제출한 신청서 상세 조회 (읽기 전용)",
)
def get_submitted_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """제출한 신청서 상세. 수정 불가 읽기 전용."""
    # TODO: application_service.get_submitted_detail(db, application_id, current_user.id) 구현 후 연결
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="준비 중인 기능입니다.",
    )
