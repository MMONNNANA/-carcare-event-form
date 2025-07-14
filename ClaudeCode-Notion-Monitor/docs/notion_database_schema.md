# Notion Database Schema

## Claude Code Sessions Database

### Required Properties

| Property Name | Type | Description | Example |
|---------------|------|-------------|---------|
| Session ID | Title | 고유 세션 식별자 | `session_1705123456` |
| Start Time | Date | 세션 시작 시간 | `2024-01-13T10:30:00` |
| Duration | Number | 세션 지속 시간 (초) | `1800` |
| Commands Count | Number | 실행된 명령어 수 | `25` |
| Status | Select | 세션 상태 | `Active`, `Completed`, `Error` |
| Model | Rich Text | 사용된 AI 모델 | `claude-sonnet-4-20250514` |
| Workspace | Rich Text | 작업 공간 경로 | `/Volumes/990 PRO 2TB/GM` |

### Optional Properties

| Property Name | Type | Description |
|---------------|------|-------------|
| End Time | Date | 세션 종료 시간 |
| Files Modified | Number | 수정된 파일 수 |
| Project Type | Select | 프로젝트 유형 |
| Tags | Multi-select | 태그 |
| Notes | Rich Text | 세션 노트 |

### Status Options
- 🟢 **Active**: 현재 진행 중인 세션
- ✅ **Completed**: 정상 완료된 세션  
- ❌ **Error**: 오류로 중단된 세션
- ⏸️ **Paused**: 일시 중지된 세션

### Project Type Options
- 🔧 **Development**: 개발 작업
- 📊 **Analysis**: 데이터 분석
- 📝 **Documentation**: 문서 작업
- 🧪 **Testing**: 테스트 작업
- 🎨 **Design**: 디자인 작업

## Database Setup Instructions

1. Notion에서 새 데이터베이스 생성
2. 위 스키마에 따라 속성(Properties) 추가
3. 통합(Integration)에 데이터베이스 접근 권한 부여
4. 데이터베이스 ID를 `.env` 파일에 설정