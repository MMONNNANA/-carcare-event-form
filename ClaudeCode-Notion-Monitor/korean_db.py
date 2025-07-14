#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def update_to_korean():
    """데이터베이스 속성을 한글로 변경"""
    print("🇰🇷 데이터베이스 속성 한글화 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 한글 속성으로 변경
        properties = {
            "상태": {
                "select": {
                    "options": [
                        {"name": "🟢 실행중", "color": "green"},
                        {"name": "🔴 중단", "color": "red"},
                        {"name": "🟡 경고", "color": "yellow"}
                    ]
                }
            },
            "유형": {
                "select": {
                    "options": [
                        {"name": "🧠 브레인", "color": "purple"},
                        {"name": "📊 모니터", "color": "blue"},
                        {"name": "🌐 서버", "color": "red"},
                        {"name": "🔄 동기화", "color": "green"},
                        {"name": "🐍 스크립트", "color": "yellow"}
                    ]
                }
            },
            "프로세스": {
                "number": {}
            },
            "CPU": {
                "number": {
                    "format": "percent"
                }
            },
            "메모리": {
                "number": {}
            },
            "시간": {
                "number": {}
            },
            "건강도": {
                "number": {}
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 한글 속성 설정 완료!")
        print("📊 변경된 속성:")
        print("  - Status → 상태")
        print("  - Type → 유형")
        print("  - PID → 프로세스")
        print("  - RAM → 메모리")
        print("  - Hours → 시간")
        print("  - Health → 건강도")
        
        return True
        
    except Exception as e:
        print(f"❌ 한글화 실패: {e}")
        return False

if __name__ == "__main__":
    success = update_to_korean()
    if success:
        print("\n🎉 한글 데이터베이스 완성!")
    else:
        print("\n💔 설정을 확인해주세요.")