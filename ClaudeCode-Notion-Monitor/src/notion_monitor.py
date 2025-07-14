import os
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv
import logging

class NotionMonitor:
    def __init__(self):
        load_dotenv("../config/.env")
        self.notion = Client(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["NOTION_DATABASE_ID"]
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        import os
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'notion_monitor.log')),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def create_session_entry(self, session_data):
        """클로드 코드 세션 데이터를 노션에 기록"""
        try:
            page_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "이름": {
                        "title": [{"text": {"content": session_data.get("session_id", "Unknown")}}]
                    },
                    "Start Time": {
                        "date": {"start": session_data.get("start_time")}
                    },
                    "Duration": {
                        "number": session_data.get("duration", 0)
                    },
                    "Commands Count": {
                        "number": session_data.get("commands_count", 0)
                    },
                    "Status": {
                        "select": {"name": session_data.get("status", "Active")}
                    },
                    "Model": {
                        "rich_text": [{"text": {"content": session_data.get("model", "Unknown")}}]
                    },
                    "Workspace": {
                        "rich_text": [{"text": {"content": session_data.get("workspace", "Unknown")}}]
                    }
                }
            }
            
            response = self.notion.pages.create(**page_data)
            self.logger.info(f"Session entry created: {response['id']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create session entry: {e}")
            return None
    
    def update_session_entry(self, page_id, update_data):
        """기존 세션 엔트리 업데이트"""
        try:
            properties = {}
            
            if "duration" in update_data:
                properties["Duration"] = {"number": update_data["duration"]}
            
            if "commands_count" in update_data:
                properties["Commands Count"] = {"number": update_data["commands_count"]}
            
            if "status" in update_data:
                properties["Status"] = {"select": {"name": update_data["status"]}}
            
            response = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            self.logger.info(f"Session updated: {page_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to update session: {e}")
            return None
    
    def get_active_sessions(self):
        """활성 세션 목록 조회"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Status",
                    "select": {"equals": "Active"}
                }
            )
            return response["results"]
            
        except Exception as e:
            self.logger.error(f"Failed to get active sessions: {e}")
            return []