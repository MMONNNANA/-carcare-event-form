#!/usr/bin/env python3

import os
import psutil
import time
from datetime import datetime, timezone
from pathlib import Path
import logging
from dotenv import load_dotenv
from notion_client import Client as NotionClient

class AutomationMonitor:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", ".env"))
        self.notion = NotionClient(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["AUTOMATION_DATABASE_ID"]
        self.tracked_processes = {}
        self.logger = self._setup_logger()
        
        # 감시할 프로세스 패턴
        self.automation_patterns = [
            "conversation_daemon.py",
            "screenshot_monitor.py", 
            "ftp_auto_monitor.py",
            "background_memory_system.py",
            "smart_calendar_system.py",
            "para_organizer.py",
            "ftpserver.py",
            "automation_monitor.py",
            "main_monitor.py",
            "claude_monitor.py",
            "realtime_memory_hook.py",
            "ftp_icloud_photos_sync.py"
        ]
    
    def _setup_logger(self):
        log_dir = Path("../logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'automation_monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def scan_automation_processes(self):
        """자동화 프로세스 스캔"""
        found_processes = []
        process_names = set()  # 중복 방지용
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                
                # 자동화 프로세스 패턴 매칭
                for pattern in self.automation_patterns:
                    if pattern in cmdline:
                        process_name = self._extract_process_name(cmdline, pattern)
                        
                        # 중복 프로세스는 메모리 합산으로 처리
                        if process_name in process_names:
                            # 기존 프로세스 찾아서 메모리 합산
                            for existing in found_processes:
                                if existing['name'] == process_name:
                                    existing['memory_mb'] += round(proc.info['memory_info'].rss / 1024 / 1024, 1)
                                    existing['memory_percent'] += round((proc.info['memory_info'].rss / (psutil.virtual_memory().total)) * 100, 2)
                                    existing['cpu_percent'] = max(existing['cpu_percent'], proc.info['cpu_percent'])
                                    break
                        else:
                            # 새 프로세스 추가
                            process_info = {
                                'pid': proc.info['pid'],
                                'name': process_name,
                                'type': self._classify_process_type(pattern),
                                'cmdline': cmdline,
                                'start_time': datetime.fromtimestamp(proc.info['create_time'], timezone.utc),
                                'cpu_percent': proc.info['cpu_percent'],
                                'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                            'memory_percent': round((proc.info['memory_info'].rss / (psutil.virtual_memory().total)) * 100, 2),
                                'status': '🟢 Running',
                                'priority': self._get_process_priority(pattern),
                                'working_dir': self._extract_working_dir(cmdline),
                                'auto_restart': self._check_auto_restart(pattern)
                            }
                            
                            found_processes.append(process_info)
                            process_names.add(process_name)
                        break
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return found_processes
    
    def _extract_process_name(self, cmdline, pattern):
        """프로세스 이름 추출"""
        if "conversation_daemon.py" in pattern:
            return "🧠 BRAIN Daemon"
        elif "screenshot_monitor.py" in pattern:
            return "📷 Screenshot"
        elif "ftp_auto_monitor.py" in pattern:
            return "📁 FTP Monitor"
        elif "background_memory_system.py" in pattern:
            return "🧠 Background Memory"
        elif "smart_calendar_system.py" in pattern:
            return "📅 Calendar"
        elif "para_organizer.py" in pattern:
            return "🗂️ PARA"
        elif "ftpserver.py" in pattern:
            return "🌐 FTP Server"
        elif "automation_monitor.py" in pattern:
            return "📊 Automation Monitor"
        elif "main_monitor.py" in pattern:
            return "📊 Claude Monitor"
        elif "claude_monitor.py" in pattern:
            return "📊 Claude Monitor"
        elif "realtime_memory_hook.py" in pattern:
            return "🧠 Realtime Memory"
        elif "ftp_icloud_photos_sync.py" in pattern:
            return "📱 FTP → iCloud Photos"
        else:
            return f"🐍 {pattern}"
    
    def _classify_process_type(self, pattern):
        """프로세스 타입 분류"""
        if "daemon" in pattern or "memory" in pattern:
            return "🧠 BRAIN"
        elif "automation_monitor" in pattern or "main_monitor" in pattern or "claude_monitor" in pattern:
            return "📊 Monitor"
        elif "server" in pattern:
            return "🌐 Server"
        elif "organizer" in pattern or "calendar" in pattern or "ftp_icloud" in pattern:
            return "🔄 Sync"
        else:
            return "🐍 Script"
    
    def _get_process_priority(self, pattern):
        """프로세스 우선순위 결정"""
        if "daemon" in pattern or "memory" in pattern:
            return "🔥 Critical"
        elif "monitor" in pattern or "server" in pattern:
            return "⚡ High"
        else:
            return "🔧 Medium"
    
    def _extract_working_dir(self, cmdline):
        """작업 디렉토리 추출"""
        if "/GM/" in cmdline:
            # GM 폴더 내 경로 추출
            parts = cmdline.split("/GM/")
            if len(parts) > 1:
                path_part = parts[1].split()[0]  # 첫 번째 인자만
                return f"/GM/{path_part}"
        return "Unknown"
    
    def _check_auto_restart(self, pattern):
        """자동 재시작 여부 확인"""
        # daemon 프로세스는 보통 자동 재시작
        return "daemon" in pattern or "server" in pattern
    
    def _get_type_emoji(self, type_name):
        """타입을 이모지로 변환"""
        if "BRAIN" in type_name:
            return "🧠"
        elif "Monitor" in type_name:
            return "📊"
        elif "Server" in type_name:
            return "🌐"
        elif "Sync" in type_name:
            return "🔄"
        else:
            return "🐍"
    
    def _get_korean_type(self, type_name):
        """타입을 한글로 변환"""
        if "BRAIN" in type_name:
            return "🧠 브레인"
        elif "Monitor" in type_name:
            return "📊 모니터"
        elif "Server" in type_name:
            return "🌐 서버"
        elif "Sync" in type_name:
            return "🔄 동기화"
        else:
            return "🐍 스크립트"
    
    def calculate_health_score(self, process_info):
        """프로세스 건강성 점수 계산 (0-100)"""
        score = 100
        
        # CPU 사용량 기준 (>50% 시 점수 감소)
        if process_info['cpu_percent'] > 50:
            score -= 20
        elif process_info['cpu_percent'] > 20:
            score -= 10
        
        # 메모리 사용량 기준 (>500MB 시 점수 감소)
        if process_info['memory_mb'] > 500:
            score -= 15
        elif process_info['memory_mb'] > 200:
            score -= 5
        
        # 가동 시간 기준 (너무 오래 실행 중이면 약간 감소)
        uptime_hours = (datetime.now(timezone.utc) - process_info['start_time']).total_seconds() / 3600
        if uptime_hours > 24:
            score -= 5
        
        return max(0, score)
    
    def find_existing_page(self, process_name):
        """노션 데이터베이스에서 기존 페이지 찾기"""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "이름",
                    "title": {
                        "equals": process_name
                    }
                }
            )
            
            if response["results"]:
                return response["results"][0]["id"]
            return None
            
        except Exception as e:
            self.logger.error(f"❌ 기존 페이지 검색 실패: {e}")
            return None
    
    def _calculate_elapsed_time(self, page_id):
        """경과시간 계산"""
        if not page_id:
            return "방금 전"
        
        try:
            # 기존 페이지에서 마지막 업데이트 시간 가져오기
            page = self.notion.pages.retrieve(page_id=page_id)
            update_property = page["properties"].get("업데이트", {})
            
            if update_property.get("date") and update_property["date"].get("start"):
                last_update = datetime.fromisoformat(update_property["date"]["start"].replace('Z', '+00:00'))
                elapsed_seconds = (datetime.now(timezone.utc) - last_update).total_seconds()
                
                if elapsed_seconds < 60:
                    return f"{int(elapsed_seconds)}초 전"
                elif elapsed_seconds < 3600:
                    return f"{int(elapsed_seconds / 60)}분 전"
                else:
                    return f"{int(elapsed_seconds / 3600)}시간 전"
            
            return "방금 전"
            
        except Exception as e:
            return "방금 전"
    
    def update_notion_database(self, processes):
        """노션 데이터베이스 업데이트"""
        self.logger.info(f"📊 {len(processes)}개 자동화 프로세스 발견")
        
        for proc in processes:
            try:
                # 건강성 점수 계산
                health_score = self.calculate_health_score(proc)
                
                # 가동 시간 계산
                uptime_hours = round((datetime.now(timezone.utc) - proc['start_time']).total_seconds() / 3600, 1)
                
                # 기존 페이지 검색
                existing_page_id = self.find_existing_page(proc['name'])
                
                # 업데이트할 속성들
                properties = {
                    "이름": {
                        "title": [{"text": {"content": proc['name']}}]
                    },
                    "유형": {
                        "select": {"name": self._get_korean_type(proc['type'])}
                    },
                    "메모리": {
                        "number": proc['memory_percent'] / 100  # 퍼센트를 소수점으로 변환
                    },
                    "CPU": {
                        "number": proc['cpu_percent'] / 100  # 퍼센트를 소수점으로 변환
                    },
                    "건강도": {
                        "number": health_score
                    },
                    "상태": {
                        "select": {"name": "🟢 실행중" if proc['status'] == "🟢 Running" else "🔴 중단"}
                    },
                    "업데이트": {
                        "date": {"start": datetime.now(timezone.utc).isoformat()}
                    },
                    "경과시간": {
                        "rich_text": [{"text": {"content": self._calculate_elapsed_time(existing_page_id)}}]
                    },
                    "제어": {
                        "checkbox": proc['status'] == "🟢 Running"  # 실행 상태와 동기화
                    }
                }
                
                if existing_page_id:
                    # 기존 페이지 업데이트
                    response = self.notion.pages.update(
                        page_id=existing_page_id,
                        properties=properties
                    )
                    self.logger.info(f"📝 프로세스 업데이트: {proc['name']}")
                else:
                    # 새 페이지 생성
                    page_data = {
                        "parent": {"database_id": self.database_id},
                        "properties": properties
                    }
                    response = self.notion.pages.create(**page_data)
                    self.logger.info(f"✅ 새 프로세스 등록: {proc['name']}")
                
            except Exception as e:
                self.logger.error(f"❌ 프로세스 업데이트 실패 {proc['name']}: {e}")
    
    def run_scan(self):
        """프로세스 스캔 실행"""
        self.logger.info("🔍 자동화 프로세스 스캔 시작...")
        
        processes = self.scan_automation_processes()
        
        if processes:
            self.update_notion_database(processes)
            self.logger.info(f"✅ {len(processes)}개 프로세스 모니터링 완료")
            
            # 요약 출력
            for proc in processes:
                self.logger.info(f"  📊 {proc['name']} | PID: {proc['pid']} | "
                               f"CPU: {proc['cpu_percent']:.1f}% | "
                               f"RAM: {proc['memory_mb']}MB")
        else:
            self.logger.warning("⚠️ 실행 중인 자동화 프로세스가 없습니다.")

if __name__ == "__main__":
    monitor = AutomationMonitor()
    monitor.run_scan()