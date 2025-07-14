#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def update_memory_to_percent():
    """메모리 속성을 퍼센트로 변경"""
    print("📊 메모리 표시를 퍼센트로 변경 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 메모리 속성을 퍼센트로 변경
        properties = {
            "메모리": {
                "number": {
                    "format": "percent"
                }
            }
        }
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 메모리 표시 변경 완료!")
        print("📋 변경사항:")
        print("  - 메모리: MB → 전체 메모리 대비 퍼센트")
        print("  - 예: 32MB → 0.4% (전체 8GB 중)")
        
        return True
        
    except Exception as e:
        print(f"❌ 변경 실패: {e}")
        return False

if __name__ == "__main__":
    success = update_memory_to_percent()
    if success:
        print("\n🎉 메모리 퍼센트 표시 완성!")
    else:
        print("\n💔 설정을 확인해주세요.")