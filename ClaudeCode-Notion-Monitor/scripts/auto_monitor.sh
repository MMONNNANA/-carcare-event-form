#!/bin/bash

# 자동화 프로세스 모니터링 정기 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🤖 자동화 프로세스 모니터링 실행"
echo "시간: $(date)"
echo "프로젝트: $PROJECT_DIR"
echo "-" * 40

cd "$PROJECT_DIR"

# 자동화 프로세스 스캔 및 노션 업데이트
python3 src/automation_monitor.py

echo "-" * 40
echo "✅ 모니터링 완료: $(date)"