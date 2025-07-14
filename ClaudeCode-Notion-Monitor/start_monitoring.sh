#!/bin/bash
# ClaudeCode Notion Monitor - 시작 스크립트

# 프로젝트 디렉토리로 이동
cd "/Volumes/990 PRO 2TB/GM/01_Projects/ClaudeCode-Notion-Monitor"

# 로그 폴더 생성
mkdir -p logs data

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 가상환경 활성화됨"
fi

# 필수 패키지 설치 확인
echo "📦 패키지 의존성 확인 중..."
python3 -c "import psutil, notion_client, python_dotenv" 2>/dev/null || {
    echo "❌ 필수 패키지 누락. 설치 중..."
    pip3 install psutil notion-client python-dotenv
}

# 환경 변수 확인
if [ ! -f "config/.env" ]; then
    echo "❌ config/.env 파일이 없습니다!"
    exit 1
fi

echo "🚀 ClaudeCode Notion Monitor 시작..."
echo "📊 효율적 모니터링 모드"
echo "🔄 30초마다 안전한 업데이트"
echo "🎛️ 노션 체크박스로 원격 제어"
echo "종료: Ctrl+C"
echo "=========================="

# 스마트 효율 모니터 실행
exec python3 src/smart_efficient_monitor.py