#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client
from collections import defaultdict

# 환경 변수 로드
load_dotenv("config/.env")

def clean_duplicate_pages():
    """노션 데이터베이스의 중복 페이지 정리"""
    print("🧹 노션 데이터베이스 중복 페이지 정리 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 데이터베이스의 모든 페이지 조회
        response = notion.databases.query(database_id=database_id)
        pages = response["results"]
        
        print(f"📊 총 {len(pages)}개 페이지 발견")
        
        # 이름별로 페이지 그룹화
        pages_by_name = defaultdict(list)
        
        for page in pages:
            # 제목 속성에서 이름 추출
            title_property = page["properties"].get("이름", {})
            if title_property.get("title"):
                page_name = title_property["title"][0]["text"]["content"]
                pages_by_name[page_name].append(page)
        
        # 중복 페이지 삭제
        deleted_count = 0
        for page_name, page_list in pages_by_name.items():
            if len(page_list) > 1:
                print(f"🔍 '{page_name}' 중복 발견: {len(page_list)}개")
                
                # 가장 최근 페이지 하나만 남기고 나머지 삭제
                sorted_pages = sorted(page_list, key=lambda x: x["created_time"], reverse=True)
                pages_to_delete = sorted_pages[1:]  # 첫 번째(최신) 제외하고 삭제
                
                for page_to_delete in pages_to_delete:
                    try:
                        notion.pages.update(
                            page_id=page_to_delete["id"],
                            archived=True
                        )
                        deleted_count += 1
                        print(f"  ❌ 삭제: {page_to_delete['id']}")
                    except Exception as e:
                        print(f"  ⚠️ 삭제 실패: {e}")
                
                print(f"  ✅ '{page_name}' 정리 완료 (1개만 남김)")
            else:
                print(f"✓ '{page_name}' - 중복 없음")
        
        print(f"\n🎉 정리 완료!")
        print(f"📊 삭제된 중복 페이지: {deleted_count}개")
        print(f"📋 남은 유니크 페이지: {len(pages_by_name)}개")
        
        return True
        
    except Exception as e:
        print(f"❌ 중복 정리 실패: {e}")
        return False

if __name__ == "__main__":
    success = clean_duplicate_pages()
    if success:
        print("\n✨ 깔끔한 데이터베이스 완성!")
    else:
        print("\n💔 설정을 확인해주세요.")