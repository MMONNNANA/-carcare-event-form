#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from notion_client import Client

# 환경 변수 로드
load_dotenv("config/.env")

def update_database_property_names():
    """데이터베이스 속성 이름을 짧게 변경"""
    print("🔧 데이터베이스 속성 이름 단축 중...")
    
    try:
        notion = Client(auth=os.environ["NOTION_TOKEN"])
        database_id = os.environ["AUTOMATION_DATABASE_ID"]
        
        # 기존 속성을 짧은 이름으로 변경
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
                        {"name": "🧠 BRAIN", "color": "purple"},
                        {"name": "📊 Monitor", "color": "blue"},
                        {"name": "🔄 Sync", "color": "green"},
                        {"name": "🗂️ Backup", "color": "orange"},
                        {"name": "🐍 Script", "color": "yellow"},
                        {"name": "📝 Log", "color": "gray"},
                        {"name": "🌐 Server", "color": "red"}
                    ]
                }
            },
            "PID": {
                "number": {
                    "format": "number"
                }
            },
            "CPU": {
                "number": {
                    "format": "percent"
                }
            },
            "RAM": {
                "number": {
                    "format": "number"
                }
            },
            "Check": {
                "date": {}
            },
            "Started": {
                "date": {}
            },
            "Hours": {
                "number": {
                    "format": "number"
                }
            },
            "Auto": {
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
            "Health": {
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
        
        print("✅ 데이터베이스 속성 이름 단축 완료!")
        print("📊 변경된 속성:")
        print("  - CPU Usage → CPU")
        print("  - Memory MB → RAM") 
        print("  - Last Check → Check")
        print("  - Start Time → Started")
        print("  - Uptime Hours → Hours")
        print("  - Command → 제거")
        print("  - Working Dir → 제거")
        print("  - Auto Restart → Auto")
        print("  - Health Score → Health")
        
        return True
        
    except Exception as e:
        print(f"❌ 속성 이름 변경 실패: {e}")
        return False

if __name__ == "__main__":
    success = update_database_property_names()
    if success:
        print("\n🎉 데이터베이스 속성 이름이 간소화되었습니다!")
    else:
        print("\n💔 설정을 확인해주세요.")