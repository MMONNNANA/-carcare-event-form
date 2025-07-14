#!/usr/bin/env python3

import sys
import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def setup_notion_database():
    """노션 데이터베이스 속성 설정"""
    print("🛠️ 노션 데이터베이스 속성 설정 시작...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["NOTION_DATABASE_ID"]
        
        # 데이터베이스 속성 정의 (기존 제목 속성 제외)
        properties = {
            "Start Time": {
                "date": {}
            },
            "Duration": {
                "number": {
                    "format": "number"
                }
            },
            "Commands Count": {
                "number": {
                    "format": "number"
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Active", "color": "green"},
                        {"name": "Completed", "color": "blue"},
                        {"name": "Error", "color": "red"},
                        {"name": "Paused", "color": "yellow"}
                    ]
                }
            },
            "Model": {
                "rich_text": {}
            },
            "Workspace": {
                "rich_text": {}
            },
            "End Time": {
                "date": {}
            },
            "Files Modified": {
                "number": {
                    "format": "number"
                }
            },
            "Project Type": {
                "select": {
                    "options": [
                        {"name": "Development", "color": "blue"},
                        {"name": "Analysis", "color": "purple"},
                        {"name": "Documentation", "color": "gray"},
                        {"name": "Testing", "color": "orange"},
                        {"name": "Design", "color": "pink"}
                    ]
                }
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 데이터베이스 속성 설정 완료!")
        print(f"📊 설정된 속성: {len(properties)}개")
        
        # 속성 목록 출력
        for prop_name in properties.keys():
            print(f"  - {prop_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 설정 실패: {e}")
        return False

if __name__ == "__main__":
    success = setup_notion_database()
    if success:
        print("\n🎉 데이터베이스 준비 완료! 이제 테스트를 진행할 수 있습니다.")
    else:
        print("\n💔 설정을 확인해주세요.")