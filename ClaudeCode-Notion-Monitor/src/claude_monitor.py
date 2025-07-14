import os
import json
import psutil
import time
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from pathlib import Path

class ClaudeActivityMonitor:
    def __init__(self, workspace_path="/Volumes/990 PRO 2TB/GM"):
        self.workspace_path = workspace_path
        self.session_data = {}
        self.active_session_id = None
        self.logger = self._setup_logger()
        self.start_time = datetime.now(timezone.utc)
        
    def _setup_logger(self):
        log_dir = Path("../logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'claude_monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def detect_claude_process(self):
        """실행 중인 클로드 코드 프로세스 감지"""
        claude_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if 'claude' in proc.info['name'].lower():
                    claude_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': proc.info['cmdline'],
                        'start_time': datetime.fromtimestamp(proc.info['create_time'], timezone.utc),
                        'status': proc.status()
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return claude_processes
    
    def start_session_tracking(self):
        """새 세션 추적 시작"""
        self.active_session_id = f"session_{int(time.time())}"
        
        session_info = {
            'session_id': self.active_session_id,
            'start_time': self.start_time.isoformat(),
            'workspace': self.workspace_path,
            'commands_count': 0,
            'files_modified': [],
            'model': self._detect_model(),
            'status': 'Active',
            'process_info': self.detect_claude_process()
        }
        
        self.session_data[self.active_session_id] = session_info
        self.logger.info(f"Started tracking session: {self.active_session_id}")
        return session_info
    
    def _detect_model(self):
        """현재 사용 중인 모델 감지"""
        try:
            # Claude Code 설정 파일에서 모델 정보 추출
            config_paths = [
                os.path.expanduser("~/.claude/config.json"),
                os.path.expanduser("~/.config/claude/config.json"),
                "/opt/homebrew/etc/claude/config.json"
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        config = json.load(f)
                        return config.get('model', 'claude-sonnet-4-20250514')
        except Exception as e:
            self.logger.warning(f"Could not detect model: {e}")
        
        return 'claude-sonnet-4-20250514'  # 기본값
    
    def update_session_activity(self, activity_type, details=None):
        """세션 활동 업데이트"""
        if not self.active_session_id:
            return
        
        session = self.session_data[self.active_session_id]
        session['commands_count'] += 1
        session['last_activity'] = datetime.now(timezone.utc).isoformat()
        
        if activity_type == 'file_modified' and details:
            session['files_modified'].append({
                'file': details.get('file_path'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'action': details.get('action', 'modified')
            })
        
        # 세션 지속 시간 계산
        start = datetime.fromisoformat(session['start_time'])
        session['duration'] = (datetime.now(timezone.utc) - start).total_seconds()
        
        self.logger.debug(f"Updated session activity: {activity_type}")
    
    def end_session(self):
        """현재 세션 종료"""
        if self.active_session_id:
            session = self.session_data[self.active_session_id]
            session['status'] = 'Completed'
            session['end_time'] = datetime.now(timezone.utc).isoformat()
            
            self.logger.info(f"Ended session: {self.active_session_id}")
            self.active_session_id = None
    
    def get_current_session_data(self):
        """현재 세션 데이터 반환"""
        if self.active_session_id:
            return self.session_data[self.active_session_id]
        return None
    
    def save_session_data(self, file_path="../data/sessions.json"):
        """세션 데이터를 파일에 저장"""
        try:
            data_dir = Path("../data")
            data_dir.mkdir(exist_ok=True)
            
            with open(data_dir / "sessions.json", 'w') as f:
                json.dump(self.session_data, f, indent=2, default=str)
                
            self.logger.info("Session data saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        self.monitor = monitor
    
    def on_modified(self, event):
        if not event.is_directory:
            self.monitor.update_session_activity('file_modified', {
                'file_path': event.src_path,
                'action': 'modified'
            })
    
    def on_created(self, event):
        if not event.is_directory:
            self.monitor.update_session_activity('file_modified', {
                'file_path': event.src_path,
                'action': 'created'
            })

def setup_file_monitoring(monitor):
    """파일 시스템 모니터링 설정"""
    event_handler = FileChangeHandler(monitor)
    observer = Observer()
    observer.schedule(event_handler, monitor.workspace_path, recursive=True)
    observer.start()
    return observer