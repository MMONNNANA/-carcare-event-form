#!/bin/bash

# Claude Code Notion Monitor 자동 시작 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Claude Code Notion Monitor 자동 시작"
echo "프로젝트 디렉토리: $PROJECT_DIR"

# 가상환경 확인 및 활성화 (선택사항)
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source "$PROJECT_DIR/venv/bin/activate"
fi

# 의존성 설치 확인
echo "📋 의존성 확인 중..."
cd "$PROJECT_DIR"
python3 -m pip install -r requirements.txt --quiet

# 환경변수 확인
if [ ! -f "$PROJECT_DIR/config/.env" ]; then
    echo "❌ .env 파일이 없습니다. config/.env 파일을 생성해주세요."
    exit 1
fi

echo "✅ 설정 완료. 모니터링 시작..."
echo "종료하려면 Ctrl+C를 눌러주세요."
echo "-" * 50

# 모니터링 시작
python3 "$PROJECT_DIR/start_monitor.py"