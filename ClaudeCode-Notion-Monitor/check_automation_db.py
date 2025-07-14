#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def check_automation_database():
    """자동화 데이터베이스 속성 확인"""
    print("🔍 자동화 데이터베이스 속성 확인 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 데이터베이스 정보 조회
        response = notion.databases.retrieve(database_id=database_id)
        
        print("📊 현재 데이터베이스 속성:")
        properties = response.get("properties", {})
        
        for prop_name, prop_config in properties.items():
            prop_type = prop_config.get("type", "unknown")
            print(f"  - {prop_name}: {prop_type}")
            
            # 제목 속성 찾기
            if prop_type == "title":
                print(f"    ✅ 제목 속성 발견: '{prop_name}'")
        
        return properties
        
    except Exception as e:
        print(f"❌ 데이터베이스 조회 실패: {e}")
        return {}

if __name__ == "__main__":
    props = check_automation_database()
    print(f"\n📈 총 {len(props)}개 속성 확인됨")