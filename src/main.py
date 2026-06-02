import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.routers.v1.router import router as v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작·종료 시 실행되는 이벤트 핸들러."""
    # ★ 시작 시: DB 연결 풀 초기화 확인
    logger.info(f"서버 시작 - 환경: {settings.ENVIRONMENT}")
    yield
    # ★ 종료 시: 필요한 정리 작업 (현재는 없음)
    logger.info("서버 종료")


app = FastAPI(
    title="Dream Lounge API",
    description="청주대학교 동아리 관리 시스템 백엔드 API",
    version="0.1.0",
    lifespan=lifespan,
    # ★ 배포 환경에서는 docs 비활성화 (보안: API 구조 노출 방지)
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ★ CORS 설정 - 배포 시 실제 도메인만 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ★ 전역 예외 핸들러 추가 (기존 코드에 없음)
# 처리되지 않은 예외가 500 에러로 노출되는 것을 막고
# 민감한 서버 내부 정보가 응답에 포함되는 것을 방지
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"처리되지 않은 예외: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
    )


app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check():
    """서버 상태 확인 (DigitalOcean 헬스체크용)."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}
