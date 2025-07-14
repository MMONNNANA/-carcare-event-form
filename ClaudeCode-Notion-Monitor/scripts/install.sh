#!/bin/bash

# Claude Code Notion Monitor 설치 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛠️ Claude Code Notion Monitor 설치 시작"
echo "프로젝트 디렉토리: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Python 버전 확인
echo "🐍 Python 버전 확인..."
python3 --version

# 의존성 설치
echo "📦 의존성 설치 중..."
python3 -m pip install -r requirements.txt

# 디렉토리 생성
echo "📁 필요 디렉토리 생성..."
mkdir -p logs data

# 환경변수 파일 확인
if [ ! -f "config/.env" ]; then
    echo "⚠️  환경변수 파일 생성 필요"
    echo "config/.env.template을 참고하여 config/.env 파일을 생성해주세요."
    echo ""
    echo "필요한 환경변수:"
    echo "- NOTION_TOKEN: 노션 API 토큰"
    echo "- NOTION_DATABASE_ID: 데이터베이스 ID"
else
    echo "✅ 환경변수 파일 확인됨"
fi

# 권한 설정
echo "🔐 실행 권한 설정..."
chmod +x start_monitor.py
chmod +x scripts/*.sh

echo ""
echo "🎉 설치 완료!"
echo ""
echo "사용법:"
echo "  모니터링 시작: ./start_monitor.py"
echo "  자동 시작:     ./scripts/auto_start.sh"
echo "  연결 테스트:   python3 test_connection.py"