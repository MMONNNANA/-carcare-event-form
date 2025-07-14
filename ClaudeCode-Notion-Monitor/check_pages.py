#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def check_existing_pages():
    """현재 데이터베이스의 모든 페이지 확인"""
    print("📋 현재 노션 데이터베이스 페이지 확인 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 모든 페이지 조회 (아카이브된 것 포함)
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "or": [
                    {"property": "이름", "title": {"is_not_empty": True}},
                ]
            }
        )
        
        print(f"📊 총 {len(response['results'])}개 페이지 발견")
        print("-" * 50)
        
        for i, page in enumerate(response['results'], 1):
            # 페이지 정보 추출
            page_id = page['id']
            archived = page.get('archived', False)
            
            # 제목 추출
            title_prop = page['properties'].get('이름', {})
            if title_prop.get('title'):
                title = title_prop['title'][0]['text']['content']
            else:
                title = "제목 없음"
            
            # 상태 추출
            status_prop = page['properties'].get('상태', {})
            if status_prop.get('select'):
                status = status_prop['select']['name']
            else:
                status = "상태 없음"
            
            # 제어 상태 추출
            control_prop = page['properties'].get('제어', {})
            control = "✅" if control_prop.get('checkbox') else "☐"
            
            # 아카이브 상태 표시
            archive_status = "🗑️ 아카이브됨" if archived else "📄 활성"
            
            print(f"{i}. {title}")
            print(f"   ID: {page_id}")
            print(f"   상태: {status} | 제어: {control} | {archive_status}")
            print()
        
        return response['results']
        
    except Exception as e:
        print(f"❌ 페이지 확인 실패: {e}")
        return []

if __name__ == "__main__":
    pages = check_existing_pages()
    print(f"✅ 총 {len(pages)}개 페이지 확인 완료")