#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def setup_automation_database_properties():
    """자동화 데이터베이스에 필요한 속성 추가"""
    print("🛠️ 자동화 모니터링 데이터베이스 속성 설정 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 필요한 속성들 정의
        properties = {
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
                        {"name": "📝 Log Processor", "color": "gray"},
                        {"name": "🌐 Server", "color": "red"}
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
        
        # 데이터베이스 업데이트
        response = notion.databases.update(
            database_id=database_id,
            properties=properties
        )
        
        print("✅ 자동화 모니터링 데이터베이스 속성 설정 완료!")
        print(f"📊 설정된 속성: {len(properties)}개")
        
        # 속성 목록 출력
        for prop_name in properties.keys():
            print(f"  - {prop_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 설정 실패: {e}")
        return False

if __name__ == "__main__":
    success = setup_automation_database_properties()
    if success:
        print("\n🎉 자동화 모니터링 데이터베이스 준비 완료!")
        print("이제 automation_monitor.py를 실행할 수 있습니다.")
    else:
        print("\n💔 설정을 확인해주세요.")