#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def simplify_database():
    """데이터베이스를 간단한 속성만 남기고 정리"""
    print("🧹 데이터베이스 간소화 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 간단한 속성만 남기기
        properties = {
            "Status": {
                "select": {
                    "options": [
                        {"name": "🟢 ON", "color": "green"},
                        {"name": "🔴 OFF", "color": "red"},
                        {"name": "🟡 WARN", "color": "yellow"}
                    ]
                }
            },
            "Type": {
                "select": {
                    "options": [
                        {"name": "🧠", "color": "purple"},
                        {"name": "📊", "color": "blue"},
                        {"name": "🌐", "color": "red"},
                        {"name": "🔄", "color": "green"},
                        {"name": "🐍", "color": "yellow"}
                    ]
                }
            },
            "PID": {
                "number": {}
            },
            "CPU": {
                "number": {
                    "format": "percent"
                }
            },
            "RAM": {
                "number": {}
            },
            "Hours": {
                "number": {}
            },
            "Health": {
                "number": {}
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 데이터베이스 간소화 완료!")
        print("📊 남은 속성: 이름, Status, Type, PID, CPU, RAM, Hours, Health")
        
        return True
        
    except Exception as e:
        print(f"❌ 간소화 실패: {e}")
        return False

if __name__ == "__main__":
    success = simplify_database()
    if success:
        print("\n🎉 깔끔한 데이터베이스 완성!")
    else:
        print("\n💔 설정을 확인해주세요.")