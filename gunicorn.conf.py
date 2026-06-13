"""Gunicorn 설정 (DigitalOcean App Platform 배포용).

실행: gunicorn src.main:app --config gunicorn.conf.py
"""

# ── 바인딩 ──────────────────────────────────────────────
# DigitalOcean App Platform은 8080 포트를 기본으로 사용
bind = "0.0.0.0:8080"

# ── 워커 ────────────────────────────────────────────────
# FastAPI(ASGI)이므로 uvicorn worker 사용 필수
worker_class = "uvicorn.workers.UvicornWorker"

# 워커 수: Basic 플랜(1 vCPU) 기준 2개
# 전용 CPU 플랜으로 올리면 (vCPU * 2 + 1) 권장
workers = 2

# ── 임시 디렉토리 (DigitalOcean 필수) ──────────────────
# /dev/shm(메모리 디스크)을 쓰면 컨테이너 환경에서 I/O 병목 회피
worker_tmp_dir = "/dev/shm"

# ── 타임아웃 ────────────────────────────────────────────
timeout = 60
graceful_timeout = 30
keepalive = 5

# ── 로깅 (DigitalOcean Runtime Logs에서 확인) ──────────
accesslog = "-"
errorlog = "-"
loglevel = "info"

# ── 워커 재활용 (메모리 누수 방지) ─────────────────────
max_requests = 1000
max_requests_jitter = 100
