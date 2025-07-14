#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def add_update_time_properties():
    """업데이트 시간 속성 추가"""
    print("⏰ 업데이트 시간 속성 추가 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 새로운 속성들 추가
        new_properties = {
            "업데이트": {
                "date": {}
            },
            "경과시간": {
                "formula": {
                    "expression": 'dateBetween(now(), prop("업데이트"), "seconds")'
                }
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=new_properties
        )
        
        print("✅ 업데이트 시간 속성 추가 완료!")
        print("📋 추가된 속성:")
        print("  - 업데이트: 마지막 업데이트 시간")
        print("  - 경과시간: 몇 초/분/시간 전 (수식)")
        
        return True
        
    except Exception as e:
        print(f"❌ 속성 추가 실패: {e}")
        return False

if __name__ == "__main__":
    success = add_update_time_properties()
    if success:
        print("\n🎉 실시간 업데이트 표시 완성!")
        print("이제 automation_monitor.py를 실행하세요.")
    else:
        print("\n💔 설정을 확인해주세요.")