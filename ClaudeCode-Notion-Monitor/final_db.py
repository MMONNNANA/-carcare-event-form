#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def setup_final_db():
    """최종 선택된 속성만으로 데이터베이스 설정"""
    print("🎯 최종 데이터베이스 구성 중...")
    print("선택된 속성: 이름, 유형, 메모리, CPU, 건강도, 상태")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 기존 속성들 삭제하고 선택된 속성만 남기기
        properties = {
            # 기존 불필요한 속성들 삭제 (None으로 설정)
            "프로세스": None,
            "시간": None,
            
            # 필요한 속성들만 유지/생성
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
            "메모리": {
                "number": {}
            },
            "CPU": {
                "number": {
                    "format": "percent"
                }
            },
            "건강도": {
                "number": {}
            },
            "상태": {
                "select": {
                    "options": [
                        {"name": "🟢 실행중", "color": "green"},
                        {"name": "🔴 중단", "color": "red"},
                        {"name": "🟡 경고", "color": "yellow"}
                    ]
                }
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 최종 데이터베이스 구성 완료!")
        print("📋 남은 속성 (6개):")
        print("  1. 이름 (제목)")
        print("  2. 유형")
        print("  3. 메모리") 
        print("  4. CPU")
        print("  5. 건강도")
        print("  6. 상태")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 실패: {e}")
        return False

if __name__ == "__main__":
    success = setup_final_db()
    if success:
        print("\n🎉 완벽한 데이터베이스 완성!")
        print("이제 automation_monitor.py를 실행하세요.")
    else:
        print("\n💔 설정을 확인해주세요.")