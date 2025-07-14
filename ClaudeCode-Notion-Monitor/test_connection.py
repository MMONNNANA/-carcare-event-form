#!/usr/bin/env python3

import sys
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv("config/.env")

sys.path.append('src')
from src.notion_client import NotionMonitor
from datetime import datetime, timezone

def test_notion_connection():
    """노션 연결 테스트"""
    print("🔗 노션 API 연결 테스트 시작...")
    
    try:
        # NotionMonitor 인스턴스 생성
        notion = NotionMonitor()
        
        # 테스트 세션 데이터 생성
        test_session = {
            "session_id": f"test_session_{int(datetime.now().timestamp())}",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "duration": 120,
            "commands_count": 5,
            "status": "Active",
            "model": "claude-sonnet-4-20250514",
            "workspace": "/Volumes/990 PRO 2TB/GM"
        }
        
        print(f"📝 테스트 데이터: {test_session}")
        
        # 노션에 엔트리 생성
        response = notion.create_session_entry(test_session)
        
        if response:
            print(f"✅ 성공! 페이지 생성됨: {response['id']}")
            print(f"🔗 페이지 URL: https://notion.so/{response['id'].replace('-', '')}")
            
            # 업데이트 테스트
            print("\n🔄 업데이트 테스트...")
            update_data = {
                "duration": 300,
                "commands_count": 10,
                "status": "Completed"
            }
            
            update_response = notion.update_session_entry(response['id'], update_data)
            if update_response:
                print("✅ 업데이트 성공!")
            else:
                print("❌ 업데이트 실패")
        else:
            print("❌ 엔트리 생성 실패")
            
    except Exception as e:
        print(f"❌ 연결 테스트 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_notion_connection()
    if success:
        print("\n🎉 노션 연동 준비 완료!")
    else:
        print("\n💔 연동 설정을 확인해주세요.")