#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def fix_elapsed_time_property():
    """경과시간 속성을 수식에서 텍스트로 변경"""
    print("🔧 경과시간 속성 수정 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 경과시간 속성을 텍스트로 변경
        properties = {
            "경과시간": {
                "rich_text": {}
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 경과시간 속성 수정 완료!")
        print("📋 변경사항:")
        print("  - 경과시간: 수식 → 텍스트 (실시간 업데이트 가능)")
        
        return True
        
    except Exception as e:
        print(f"❌ 속성 수정 실패: {e}")
        return False

if __name__ == "__main__":
    success = fix_elapsed_time_property()
    if success:
        print("\n🎉 실시간 경과시간 표시 준비 완료!")
    else:
        print("\n💔 설정을 확인해주세요.")