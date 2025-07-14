#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def clean_and_setup_korean_db():
    """기존 속성 삭제하고 한글 속성만 설정"""
    print("🧹 데이터베이스 완전 정리 후 한글 설정 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 먼저 기존 데이터베이스 구조 확인
        db_info = notion.databases.retrieve(database_id=database_id)
        current_props = db_info.get("properties", {})
        
        print("🔍 현재 속성들:")
        for prop_name in current_props.keys():
            print(f"  - {prop_name}")
        
        # 삭제할 영문 속성들 (빈 객체로 설정하면 삭제됨)
        properties_to_remove = {}
        for prop_name in current_props.keys():
            if prop_name not in ["이름"]:  # 제목 속성은 유지
                properties_to_remove[prop_name] = None
        
        # 새로운 한글 속성들
        korean_properties = {
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
        
        # 기존 속성 삭제 + 새 속성 추가
        all_properties = {**properties_to_remove, **korean_properties}
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=all_properties
        )
        
        print("✅ 데이터베이스 완전 정리 완료!")
        print("🇰🇷 한글 속성만 남음:")
        print("  - 이름 (제목)")
        print("  - 상태")
        print("  - 유형") 
        print("  - 프로세스")
        print("  - CPU")
        print("  - 메모리")
        print("  - 시간")
        print("  - 건강도")
        
        return True
        
    except Exception as e:
        print(f"❌ 정리 실패: {e}")
        return False

if __name__ == "__main__":
    success = clean_and_setup_korean_db()
    if success:
        print("\n🎉 깔끔한 한글 데이터베이스 완성!")
        print("이제 automation_monitor.py를 실행하세요.")
    else:
        print("\n💔 설정을 확인해주세요.")