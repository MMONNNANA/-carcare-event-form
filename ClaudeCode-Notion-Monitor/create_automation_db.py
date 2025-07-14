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
        
        # 직접 데이터베이스 생성 (workspace root에)
        database_data = {
            "parent": {
                "type": "workspace",
                "workspace": True
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "🤖 자동화 프로세서 현황"
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
                "Memory MB": {
                    "number": {
                        "format": "number"
                    }
                },
                "Last Check": {
                    "date": {}
                },
                "Start Time": {
                    "date": {}
                },
                "Uptime Hours": {
                    "number": {
                        "format": "number"
                    }
                },
                "Command": {
                    "rich_text": {}
                },
                "Working Dir": {
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
    else:
        print("\n💔 설정을 확인해주세요.")