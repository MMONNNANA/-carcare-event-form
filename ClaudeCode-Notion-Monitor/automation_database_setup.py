#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def create_automation_database():
    """자동화 프로세서 현황 모니터링 데이터베이스 생성"""
    print("🛠️ 자동화 프로세서 현황 데이터베이스 생성 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        
        # 먼저 페이지를 생성
        page_data = {
            "parent": {
                "type": "page_id", 
                "page_id": "22fea5e4a83280268a48cd5cca639e5d"
            },
            "properties": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "자동화 프로세서 현황 모니터링"
                        }
                    }
                ]
            }
        }
        
        page_response = notion.pages.create(**page_data)
        print(f"📄 페이지 생성됨: {page_response['id']}")
        
        # 데이터베이스 생성
        database_data = {
            "parent": {
                "type": "page_id",
                "page_id": page_response['id']
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "자동화 프로세서 현황 모니터링"
                    }
                }
            ],
            "properties": {
                "Process Name": {
                    "title": {}
                },
                "Status": {
                    "select": {
                        "options": [
                            {"name": "🟢 Running", "color": "green"},
                            {"name": "🔴 Stopped", "color": "red"},
                            {"name": "🟡 Warning", "color": "yellow"},
                            {"name": "🔵 Idle", "color": "blue"},
                            {"name": "⚫ Unknown", "color": "gray"}
                        ]
                    }
                },
                "Type": {
                    "select": {
                        "options": [
                            {"name": "🧠 BRAIN System", "color": "purple"},
                            {"name": "📊 Monitor", "color": "blue"},
                            {"name": "🔄 Sync", "color": "green"},
                            {"name": "🗂️ Backup", "color": "orange"},
                            {"name": "🐍 Python Script", "color": "yellow"},
                            {"name": "📝 Log Processor", "color": "gray"}
                        ]
                    }
                },
                "PID": {
                    "number": {
                        "format": "number"
                    }
                },
                "CPU Usage": {
                    "number": {
                        "format": "percent"
                    }
                },
                "Memory Usage": {
                    "rich_text": {}
                },
                "Last Check": {
                    "date": {}
                },
                "Start Time": {
                    "date": {}
                },
                "Uptime": {
                    "rich_text": {}
                },
                "Command": {
                    "rich_text": {}
                },
                "Working Directory": {
                    "rich_text": {}
                },
                "Log File": {
                    "rich_text": {}
                },
                "Auto Restart": {
                    "checkbox": {}
                },
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "🔥 Critical", "color": "red"},
                            {"name": "⚡ High", "color": "orange"},
                            {"name": "🔧 Medium", "color": "yellow"},
                            {"name": "📋 Low", "color": "gray"}
                        ]
                    }
                },
                "Description": {
                    "rich_text": {}
                },
                "Dependencies": {
                    "rich_text": {}
                },
                "Health Score": {
                    "number": {
                        "format": "number"
                    }
                }
            }
        }
        
        response = notion.databases.create(**database_data)
        
        print("✅ 자동화 프로세서 데이터베이스 생성 완료!")
        print(f"📊 데이터베이스 ID: {response['id']}")
        print(f"🔗 데이터베이스 URL: https://notion.so/{response['id'].replace('-', '')}")
        
        # 환경변수에 추가
        with open("config/.env", "a") as f:
            f.write(f"\nAUTOMATION_DATABASE_ID={response['id']}\n")
        
        print("💾 데이터베이스 ID가 .env 파일에 저장되었습니다.")
        
        return response['id']
        
    except Exception as e:
        print(f"❌ 데이터베이스 생성 실패: {e}")
        return None

if __name__ == "__main__":
    db_id = create_automation_database()
    if db_id:
        print("\n🎉 자동화 프로세서 모니터링 시스템 준비 완료!")
        print("\n📋 모니터링할 속성:")
        print("  - Process Name: 프로세스 이름")
        print("  - Status: 실행 상태")
        print("  - Type: 프로세스 유형")
        print("  - PID: 프로세스 ID")
        print("  - CPU/Memory Usage: 리소스 사용량")
        print("  - Uptime: 가동 시간")
        print("  - Health Score: 건강성 점수")
    else:
        print("\n💔 설정을 확인해주세요.")