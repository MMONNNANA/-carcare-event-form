# 📸 FTP → iCloud Photos 실시간 동기화 시스템

Sony 카메라 → FTP → Photos 앱 → iCloud → iPhone 자동 동기화

## 🎯 목적
- **현장 촬영**: 사진 촬영 후 즉시 iPhone에서 확인
- **백업**: 모든 사진을 iCloud에 자동 백업
- **편의성**: 수동 작업 없이 완전 자동화

## ⚡ 배치 처리 최적화
- **즉시 처리**: 파일이 있으면 바로 처리, 최대 10개까지 한 번에
- **안정적 동기화**: 배치 완료 후 일괄 iCloud 동기화
- **실시간 감지**: 새 파일 즉시 감지 및 큐 추가

## 📁 지원 형식
- **사진**: .jpg, .jpeg, .png, .heic, .heif
- **동영상**: .mov, .mp4, .avi, .mkv

## 🔄 동작 플로우
1. Sony 카메라 → FTP 업로드
2. 실시간 파일 감지 (watchdog)
3. 중복 체크 (SQLite 기반)
4. Photos 앱 자동 추가
5. iCloud 동기화 트리거
6. iPhone에서 확인 가능

## 🚀 사용법

### 실시간 동기화 (자동 실행)
```bash
# 서비스로 자동 실행 중
# 새 파일이 FTP에 업로드되면 자동 처리
```

### 기존 파일 일괄 동기화
```bash
# 과거 → 최근 순으로 모든 기존 파일 업로드
python3 ftp_icloud_photos_sync.py --sync-existing
```

### 수동 실행
```bash
# 직접 실행 (테스트용)
python3 ftp_icloud_photos_sync.py
```

## 📊 모니터링
- **노션 자동화 모니터**: 실시간 상태 확인
- **로그**: `/Volumes/990 PRO 2TB/GM/logs/ftp_icloud_sync.log`
- **데이터베이스**: `sync_history.db` (업로드 이력 추적)

## 🔧 서비스 관리
```bash
# 서비스 중지
launchctl unload ~/Library/LaunchAgents/com.gm.ftp-icloud-photos.plist

# 서비스 시작
launchctl load ~/Library/LaunchAgents/com.gm.ftp-icloud-photos.plist

# 서비스 상태 확인
launchctl print gui/$(id -u)/com.gm.ftp-icloud-photos
```

## 📈 성능 특징
- **메모리 사용량**: ~15MB (매우 경량)
- **CPU 사용량**: 0% (대기 시)
- **처리 속도**: 사진 1장당 ~2초 (Photos 앱 추가 + iCloud 동기화)

## 🛡️ 안전 기능
- **원본 보존**: FTP 파일은 수정/이동/삭제 안함
- **중복 방지**: 해시값 기반 중복 체크
- **에러 처리**: 실패 시 재시도 로직
- **로그 기록**: 모든 작업 상세 로그

## 🔮 다음 단계
- **FTP 외부 접속**: 원격에서도 사진 업로드 가능하도록 확장 예정