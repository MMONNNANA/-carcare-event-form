#!/usr/bin/env python3

import os
import psutil
import subprocess
import signal
from datetime import datetime, timezone
from pathlib import Path
import logging
from dotenv import load_dotenv
from notion_client import Client as NotionClient

class ProcessController:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", ".env"))
        self.notion = NotionClient(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["AUTOMATION_DATABASE_ID"]
        self.logger = self._setup_logger()
        
        # 제어 가능한 프로세스 명령어 매핑
        self.process_commands = {
            "📷 Screenshot": {
                "start": "python3 /Volumes/990\\ PRO\\ 2TB/GM/03_Areas/System_Automation/screenshot_monitor.py &",
                "pattern": "screenshot_monitor.py"
            },
            "🧠 BRAIN Daemon": {
                "start": "python3 /Volumes/990\\ PRO\\ 2TB/GM/02_Projects/Claude_Personal_Assistant/conversation_daemon.py start &",
                "pattern": "conversation_daemon.py"
            }
            # FTP Server는 외부 앱이라 제어하지 않음
        }
    
    def _setup_logger(self):
        log_dir = Path("../logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'process_controller.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_control_states(self):
        """노션에서 제어 상태 확인"""
        try:
            response = self.notion.databases.query(database_id=self.database_id)
            control_states = {}
            
            for page in response["results"]:
                # 프로세스 이름 가져오기
                title_property = page["properties"].get("이름", {})
                if title_property.get("title"):
                    process_name = title_property["title"][0]["text"]["content"]
                    
                    # 제어 체크박스 상태 가져오기
                    control_property = page["properties"].get("제어", {})
                    is_enabled = control_property.get("checkbox", False)
                    
                    control_states[process_name] = is_enabled
            
            return control_states
            
        except Exception as e:
            self.logger.error(f"❌ 제어 상태 확인 실패: {e}")
            return {}
    
    def is_process_running(self, pattern):
        """프로세스가 실행 중인지 확인"""
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                if pattern in cmdline:
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_process(self, process_name):
        """프로세스 시작"""
        if process_name not in self.process_commands:
            self.logger.warning(f"⚠️ 제어 불가능한 프로세스: {process_name}")
            return False
        
        try:
            command = self.process_commands[process_name]["start"]
            subprocess.Popen(command, shell=True)
            self.logger.info(f"🚀 프로세스 시작: {process_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 프로세스 시작 실패 {process_name}: {e}")
            return False
    
    def stop_process(self, process_name):
        """프로세스 중단"""
        if process_name not in self.process_commands:
            self.logger.warning(f"⚠️ 제어 불가능한 프로세스: {process_name}")
            return False
        
        try:
            pattern = self.process_commands[process_name]["pattern"]
            pid = self.is_process_running(pattern)
            
            if pid:
                os.kill(pid, signal.SIGTERM)
                self.logger.info(f"🛑 프로세스 중단: {process_name} (PID: {pid})")
                return True
            else:
                self.logger.info(f"ℹ️ 프로세스가 이미 중단됨: {process_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ 프로세스 중단 실패 {process_name}: {e}")
            return False
    
    def control_processes(self):
        """노션 설정에 따라 프로세스 제어"""
        self.logger.info("🎛️ 프로세스 제어 시작...")
        
        control_states = self.get_control_states()
        
        for process_name, should_run in control_states.items():
            if process_name not in self.process_commands:
                continue
            
            pattern = self.process_commands[process_name]["pattern"]
            is_running = self.is_process_running(pattern) is not None
            
            if should_run and not is_running:
                # 체크되었는데 실행 안됨 → 시작
                self.logger.info(f"✅ {process_name} 시작 요청")
                self.start_process(process_name)
                
            elif not should_run and is_running:
                # 체크 해제되었는데 실행 중 → 중단
                self.logger.info(f"☐ {process_name} 중단 요청")
                self.stop_process(process_name)
                
            else:
                # 상태 일치 → 유지
                status = "실행 중" if is_running else "중단됨"
                self.logger.debug(f"🔄 {process_name}: {status} (설정과 일치)")
        
        self.logger.info("🎛️ 프로세스 제어 완료")

if __name__ == "__main__":
    controller = ProcessController()
    controller.control_processes()