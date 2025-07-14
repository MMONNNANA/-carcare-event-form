#!/bin/bash
# ClaudeCode Notion Monitor - 시작 프로그램 설치 스크립트

PLIST_FILE="com.claudecode.notionmonitor.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🔧 ClaudeCode Notion Monitor 시작 프로그램 설치 중..."

# LaunchAgents 디렉토리 생성
mkdir -p "$LAUNCHAGENTS_DIR"

# plist 파일 복사
cp "$PLIST_FILE" "$LAUNCHAGENTS_DIR/"

# 권한 설정
chmod 644 "$LAUNCHAGENTS_DIR/$PLIST_FILE"

# 기존 서비스 언로드 (있는 경우)
launchctl unload "$LAUNCHAGENTS_DIR/$PLIST_FILE" 2>/dev/null

# 새 서비스 로드
launchctl load "$LAUNCHAGENTS_DIR/$PLIST_FILE"

# 상태 확인
if launchctl list | grep -q "com.claudecode.notionmonitor"; then
    echo "✅ 시작 프로그램 설치 완료!"
    echo "📋 상태: $(launchctl list | grep com.claudecode.notionmonitor)"
    echo ""
    echo "🎛️ 제어 명령어:"
    echo "  시작: launchctl start com.claudecode.notionmonitor"
    echo "  중지: launchctl stop com.claudecode.notionmonitor"
    echo "  제거: launchctl unload ~/Library/LaunchAgents/com.claudecode.notionmonitor.plist"
    echo ""
    echo "📊 로그 확인:"
    echo "  실행 로그: tail -f logs/startup.log"
    echo "  에러 로그: tail -f logs/startup.error.log"
else
    echo "❌ 설치 실패. 다시 시도해 주세요."
    exit 1
fi