#!/usr/bin/env python3

import os
import psutil
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import logging
from dotenv import load_dotenv
from notion_client import Client as NotionClient

class EfficientMonitor:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", ".env"))
        self.notion = NotionClient(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["AUTOMATION_DATABASE_ID"]
        self.logger = self._setup_logger()
        
        # 등록된 프로세스 목록 (고정) - 최적화됨
        self.registered_processes = {
            "📊 Automation Monitor": ["efficient_monitor.py", "smart_efficient_monitor.py"],
            "📷 Screenshot": ["screenshot_monitor.py"], 
            "🌐 FTP Server": ["ftpserver.py"],
            "🧠 BRAIN Daemon": ["conversation_daemon.py"],
            "🧠 Background Memory": ["background_memory_system.py"],
            "🧠 Realtime Memory": ["realtime_memory_hook.py"],
            "🧠 Thinking Triggers": ["thinking_triggers.py"]
        }
        
        # 노션 페이지 ID 캐시
        self.page_cache = {}
        self.cache_file = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "page_cache.json"))
        self.load_cache()
    
    def _setup_logger(self):
        log_dir = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"))
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'efficient_monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def load_cache(self):
        """페이지 ID 캐시 로드"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.page_cache = json.load(f)
                self.logger.info(f"💾 캐시 로드됨: {len(self.page_cache)}개 페이지")
        except Exception as e:
            self.logger.warning(f"⚠️ 캐시 로드 실패: {e}")
            self.page_cache = {}
    
    def save_cache(self):
        """페이지 ID 캐시 저장"""
        try:
            self.cache_file.parent.mkdir(exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.page_cache, f)
        except Exception as e:
            self.logger.error(f"❌ 캐시 저장 실패: {e}")
    
    def get_process_status(self, patterns):
        """특정 프로세스 상태 조회 (빠른 검색)"""
        total_memory = 0
        total_cpu = 0
        process_count = 0
        pids = []
        
        # patterns가 문자열이면 리스트로 변환
        if isinstance(patterns, str):
            patterns = [patterns]
        
        for proc in psutil.process_iter(['pid', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                # 패턴 목록 중 하나라도 매치되면 포함
                if any(pattern in cmdline for pattern in patterns):
                    total_memory += proc.info['memory_info'].rss
                    total_cpu = max(total_cpu, proc.info['cpu_percent'])
                    process_count += 1
                    pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if process_count > 0:
            memory_mb = round(total_memory / 1024 / 1024, 1)
            memory_percent = round((total_memory / psutil.virtual_memory().total) * 100, 2)
            return {
                'running': True,
                'memory_mb': memory_mb,
                'memory_percent': memory_percent,
                'cpu_percent': total_cpu,
                'process_count': process_count,
                'pids': pids
            }
        else:
            return {
                'running': False,
                'memory_mb': 0,
                'memory_percent': 0,
                'cpu_percent': 0,
                'process_count': 0,
                'pids': []
            }
    
    def get_page_id(self, process_name):
        """캐시된 페이지 ID 가져오기"""
        if process_name in self.page_cache:
            return self.page_cache[process_name]
        
        # 캐시에 없으면 노션에서 검색
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "이름",
                    "title": {"equals": process_name}
                }
            )
            
            if response["results"]:
                page_id = response["results"][0]["id"]
                self.page_cache[process_name] = page_id
                self.save_cache()
                return page_id
        except Exception as e:
            self.logger.error(f"❌ 페이지 검색 실패 {process_name}: {e}")
        
        return None
    
    def calculate_health_score(self, status):
        """건강성 점수 계산"""
        if not status['running']:
            return 0
        
        score = 100
        
        # CPU 기준
        if status['cpu_percent'] > 50:
            score -= 20
        elif status['cpu_percent'] > 20:
            score -= 10
        
        # 메모리 기준 (퍼센트)
        if status['memory_percent'] > 2.0:  # 2% 이상
            score -= 15
        elif status['memory_percent'] > 1.0:  # 1% 이상
            score -= 5
        
        return max(0, score)
    
    def batch_update_notion(self):
        """배치로 노션 업데이트 (효율적) - 페이지 삭제 절대 금지"""
        self.logger.info("🔄 효율적 상태 업데이트 시작...")
        
        update_count = 0
        current_time = datetime.now(timezone.utc).isoformat()
        
        for process_name, patterns in self.registered_processes.items():
            try:
                # 프로세스 상태 조회
                status = self.get_process_status(patterns)
                
                # 페이지 ID 가져오기 (존재하지 않으면 경고만 출력, 절대 삭제하지 않음)
                page_id = self.get_page_id(process_name)
                if not page_id:
                    self.logger.warning(f"⚠️ 페이지 없음 (삭제 금지): {process_name}")
                    continue
                
                # 건강성 점수 계산
                health_score = self.calculate_health_score(status)
                
                # 프로세스 유형 결정
                if "BRAIN" in process_name or "Memory" in process_name:
                    process_type = "🧠 브레인"
                elif "Monitor" in process_name:
                    process_type = "📊 모니터"
                elif "Server" in process_name:
                    process_type = "🌐 서버"
                else:
                    process_type = "🐍 스크립트"
                
                # 업데이트 속성
                properties = {
                    "유형": {"select": {"name": process_type}},
                    "메모리": {"number": status['memory_percent'] / 100},
                    "CPU": {"number": status['cpu_percent'] / 100},
                    "건강도": {"number": health_score},
                    "상태": {"select": {"name": "🟢 실행중" if status['running'] else "🔴 중단"}},
                    "업데이트": {"date": {"start": current_time}},
                    "경과시간": {"rich_text": [{"text": {"content": "방금 전"}}]},
                    "제어": {"checkbox": status['running']}
                }
                
                # 노션 업데이트 (rate limit 고려)
                try:
                    self.notion.pages.update(page_id=page_id, properties=properties)
                    update_count += 1
                    # 대기 시간 최소화 (0.2초)
                    time.sleep(0.2)
                except Exception as api_error:
                    if "rate_limited" in str(api_error).lower():
                        self.logger.warning(f"⚠️ API 제한 감지, 10초 대기...")
                        time.sleep(10)
                    else:
                        raise api_error
                
                # 로그 출력
                status_emoji = "🟢" if status['running'] else "🔴"
                self.logger.info(f"{status_emoji} {process_name}: {status['memory_percent']:.2f}% RAM, {status['cpu_percent']:.1f}% CPU")
                
            except Exception as e:
                self.logger.error(f"❌ 업데이트 실패 {process_name}: {e}")
        
        self.logger.info(f"✅ 배치 업데이트 완료: {update_count}/{len(self.registered_processes)}개")
        return update_count

if __name__ == "__main__":
    monitor = EfficientMonitor()
    monitor.batch_update_notion()