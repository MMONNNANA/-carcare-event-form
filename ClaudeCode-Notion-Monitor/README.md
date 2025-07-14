# 📊 ClaudeCode Notion Monitor

효율적인 자동화 프로세스 모니터링 및 노션 연동 시스템

## 🚀 빠른 시작

```bash
# 즉시 실행
./start_monitoring.sh

# 시작 프로그램으로 설치
./install_startup.sh
```

## ✨ 주요 기능

- 🎛️ **노션 원격 제어**: 체크박스로 프로세스 on/off
- 📊 **실시간 모니터링**: CPU, 메모리, 상태 추적  
- ⚡ **효율적 동작**: 등록된 프로세스만 모니터링
- 💾 **캐시 최적화**: 페이지 ID 캐싱으로 성능 향상
- 🔄 **30초 업데이트**: API 제한 고려한 안전한 업데이트

## 📁 핵심 파일

- `src/smart_efficient_monitor.py` - 메인 모니터링 시스템
- `src/efficient_monitor.py` - 최적화된 스캔 엔진
- `src/process_controller.py` - 노션 기반 프로세스 제어
- `start_monitoring.sh` - 실행 스크립트
- `install_startup.sh` - 시작 프로그램 설치

## 🎯 모니터링 대상

1. 📊 Automation Monitor
2. 📷 Screenshot  
3. 🌐 FTP Server
4. 🧠 BRAIN Daemon
5. 🧠 Memory System

## 🔧 제어 명령어

```bash
# 서비스 제어
launchctl start com.claudecode.notionmonitor
launchctl stop com.claudecode.notionmonitor

# 로그 확인
tail -f logs/startup.log
tail -f logs/startup.error.log
```

## 🚫 안전 규칙

- **페이지 삭제 절대 금지** - 기존 노션 페이지 보호
- **업데이트만 수행** - 상태 정보만 갱신
- **사용자 승인 필요** - 모든 삭제 작업