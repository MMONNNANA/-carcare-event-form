#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def add_control_switch():
    """자동화 제어 스위치(체크박스) 속성 추가"""
    print("🎛️ 자동화 제어 스위치 추가 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 제어 스위치 속성 추가
        new_properties = {
            "제어": {
                "checkbox": {}
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=new_properties
        )
        
        print("✅ 제어 스위치 추가 완료!")
        print("📋 추가된 기능:")
        print("  - 제어: 체크박스 (ON/OFF 스위치)")
        print("  - ✅ 체크: 자동화 시스템 실행 허용")
        print("  - ☐ 해제: 자동화 시스템 중단")
        
        return True
        
    except Exception as e:
        print(f"❌ 스위치 추가 실패: {e}")
        return False

if __name__ == "__main__":
    success = add_control_switch()
    if success:
        print("\n🎉 자동화 제어 시스템 준비 완료!")
        print("이제 노션에서 체크박스로 각 시스템을 제어할 수 있습니다!")
    else:
        print("\n💔 설정을 확인해주세요.")