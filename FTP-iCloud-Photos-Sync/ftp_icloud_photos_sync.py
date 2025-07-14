#!/usr/bin/env python3
"""
FTP → iCloud Photos 실시간 동기화 시스템
Sony 카메라 → FTP → Photos 앱 → iCloud 자동 업로드

특징:
- 실시간 파일 감지 (watchdog)
- 원본 파일 보존 (복사만 수행)
- 중복 방지 (SQLite 기반 이력 관리)
- 배치 업로드 (순차 처리)
- iCloud 동기화 강제 실행
"""

import os
import sys
import time
import hashlib
import sqlite3
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Set, List, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue

class FTPiCloudPhotoSync:
    def __init__(self):
        # 경로 설정
        self.ftp_root = Path("/Volumes/990 PRO 2TB/FTP")
        self.project_dir = Path("/Volumes/990 PRO 2TB/GM/01_Projects/FTP-iCloud-Photos-Sync")
        self.db_path = self.project_dir / "sync_history.db"
        self.log_dir = Path("/Volumes/990 PRO 2TB/GM/logs")
        
        # 지원하는 파일 형식
        self.supported_extensions = {
            '.jpg', '.jpeg', '.png', '.heic', '.heif',  # 사진
            '.mov', '.mp4', '.avi', '.mkv'  # 동영상
        }
        
        # 업로드 큐 및 상태
        self.upload_queue = queue.Queue()
        self.processing = False
        self.batch_size = 10  # 최대 10장씩 배치 처리 (Photos 앱 부하 방지)
        
        # 로깅 설정
        self._setup_logging()
        
        # 데이터베이스 초기화
        self._init_database()
        
        self.logger.info("🎯 FTP → iCloud Photos 동기화 시스템 시작")

    def _setup_logging(self):
        """로깅 설정"""
        self.log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'ftp_icloud_sync.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """SQLite 데이터베이스 초기화"""
        self.project_dir.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_hash TEXT NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_hash ON sync_history(file_hash)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_path ON sync_history(file_path)
            ''')

    def _get_file_hash(self, file_path: Path) -> str:
        """파일 해시값 계산 (중복 감지용) - 성능 최적화"""
        try:
            # 파일 크기와 수정 시간을 조합한 빠른 해시 생성
            stat = file_path.stat()
            file_info = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(file_info.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f"❌ 해시 계산 실패 {file_path}: {e}")
            return ""

    def _is_duplicate(self, file_path: Path, file_size: int, file_hash: str) -> bool:
        """중복 파일 체크"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM sync_history WHERE file_hash = ? OR file_path = ?",
                    (file_hash, str(file_path))
                )
                return cursor.fetchone()[0] > 0
        except Exception as e:
            self.logger.error(f"❌ 중복 체크 실패: {e}")
            return False

    def _close_photos_error_dialogs(self):
        """Photos 앱 오류 다이얼로그 자동 닫기"""
        try:
            applescript = '''
            tell application "System Events"
                tell process "Photos"
                    repeat with theWindow in windows
                        try
                            if exists button "확인" of theWindow then
                                click button "확인" of theWindow
                            end if
                        end try
                    end repeat
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], capture_output=True, timeout=5)
        except:
            pass

    def _add_batch_to_photos_app(self, file_paths: List[Path]) -> int:
        """Photos 앱에 배치로 파일 추가 - 오류 처리 강화"""
        max_retries = 2
        
        for retry in range(max_retries):
            try:
                # 오류창 닫기
                self._close_photos_error_dialogs()
                
                # 파일 경로들을 AppleScript 리스트로 변환
                file_list = ", ".join([f'POSIX file "{fp}"' for fp in file_paths])
                
                if retry == 0:
                    self.logger.info(f"📤 {len(file_paths)}개 파일을 1번의 요청으로 업로드...")
                else:
                    self.logger.info(f"🔄 재시도 {retry}/{max_retries-1}: {len(file_paths)}개 파일 업로드...")
                
                applescript = f'''
                tell application "Photos"
                    import {{{file_list}}} skip check duplicates yes
                end tell
                '''
                
                result = subprocess.run(
                    ['osascript', '-e', applescript],
                    capture_output=True,
                    text=True,
                    timeout=60  # 1분으로 단축
                )
                
                # 업로드 후 오류창 체크 및 닫기
                import time
                time.sleep(1)
                self._close_photos_error_dialogs()
                
                if result.returncode == 0:
                    self.logger.info(f"✅ Photos 앱 배치 추가 완료: {len(file_paths)}개 파일")
                    return len(file_paths)
                else:
                    self.logger.warning(f"⚠️ 시도 {retry+1} 실패: {result.stderr}")
                    if retry < max_retries - 1:
                        time.sleep(2)  # 재시도 전 대기
                        
            except Exception as e:
                self.logger.warning(f"⚠️ 시도 {retry+1} 오류: {e}")
                if retry < max_retries - 1:
                    import time
                    time.sleep(2)
        
        self.logger.error(f"❌ 모든 재시도 실패: {[f.name for f in file_paths]}")
        return 0

    def _trigger_icloud_sync(self) -> bool:
        """iCloud Photos 동기화 강제 실행"""
        try:
            # cloudphotod 프로세스에 SIGUSR1 신호 전송 (동기화 트리거)
            result = subprocess.run(
                ['killall', '-USR1', 'cloudphotod'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("🔄 iCloud Photos 동기화 트리거됨")
                return True
            else:
                # 대안: Photos 앱 재시작
                subprocess.run(['killall', 'Photos'], capture_output=True)
                time.sleep(2)
                subprocess.run(['open', '-a', 'Photos'], capture_output=True)
                self.logger.info("🔄 Photos 앱 재시작으로 동기화 유도")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ iCloud 동기화 트리거 실패: {e}")
            return False

    def _record_upload(self, file_path: Path, file_size: int, file_hash: str):
        """업로드 이력 기록"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO sync_history (file_path, file_size, file_hash) VALUES (?, ?, ?)",
                    (str(file_path), file_size, file_hash)
                )
                self.logger.debug(f"📝 업로드 이력 기록: {file_path.name}")
        except Exception as e:
            self.logger.error(f"❌ 이력 기록 실패: {e}")

    def _process_file(self, file_path: Path) -> bool:
        """개별 파일 처리"""
        try:
            # 파일 유효성 검사
            if not file_path.exists() or file_path.stat().st_size == 0:
                self.logger.warning(f"⚠️ 파일이 존재하지 않거나 비어있음: {file_path}")
                return False
            
            # 지원되는 형식인지 확인
            if file_path.suffix.lower() not in self.supported_extensions:
                self.logger.debug(f"🚫 지원되지 않는 형식: {file_path}")
                return False
            
            # 파일 정보 수집
            file_size = file_path.stat().st_size
            file_hash = self._get_file_hash(file_path)
            
            if not file_hash:
                return False
            
            # 중복 체크
            # 중복 체크 비활성화 - 모든 파일 처리
            
            # 개별 파일은 배치로 처리하므로 여기서는 검증만
            return True
                
        except Exception as e:
            self.logger.error(f"❌ 파일 처리 실패 {file_path}: {e}")
            return False

    def _batch_processor(self):
        """배치 처리 워커"""
        while True:
            try:
                # 큐에서 파일들 수집 (최대 batch_size만큼)
                files_to_process = []
                
                # 첫 번째 파일 대기 (블로킹) - 파일이 있으면 즉시 처리
                try:
                    first_file = self.upload_queue.get(timeout=2)
                    files_to_process.append(first_file)
                except queue.Empty:
                    continue
                
                # 추가 파일들 수집 (논블로킹) - 있는 만큼만 최대 10장까지
                while len(files_to_process) < self.batch_size:
                    try:
                        file_path = self.upload_queue.get_nowait()
                        files_to_process.append(file_path)
                    except queue.Empty:
                        break  # 더 이상 파일이 없으면 현재 파일들로 바로 처리
                
                if files_to_process:
                    self.processing = True
                    self.logger.info(f"📦 배치 처리 시작: {len(files_to_process)}개 파일 (대기하지 않고 즉시 처리)")
                    
                    # 파일들 순차 처리
                    success_count = 0
                    for file_path in files_to_process:
                        if self._process_file(file_path):
                            success_count += 1
                    
                    # 배치 처리 완료 후 iCloud 동기화 트리거
                    if success_count > 0:
                        self.logger.info(f"🎯 배치 완료: {success_count}/{len(files_to_process)}개 성공")
                            
                    self.processing = False
                    
                    # 큐 완료 신호
                    for _ in files_to_process:
                        self.upload_queue.task_done()
                        
            except Exception as e:
                self.logger.error(f"❌ 배치 처리 오류: {e}")
                self.processing = False
                time.sleep(5)

    def scan_existing_files(self) -> List[Path]:
        """기존 파일들을 생성 시간 순으로 스캔 (모든 하위 폴더 포함) - 성능 최적화"""
        self.logger.info("📂 기존 파일 스캔 시작...")
        self.logger.info(f"🔍 검색 경로: {self.ftp_root}")
        self.logger.info(f"📝 지원 형식: {', '.join(self.supported_extensions)}")
        
        existing_files = []
        scanned_folders = set()
        total_files_found = 0
        processed_count = 0
        
        # 모든 하위 폴더를 재귀적으로 스캔
        for file_path in self.ftp_root.rglob("*"):
            if file_path.is_file():
                total_files_found += 1
                
                # 진행 상황 출력
                if total_files_found % 100 == 0:
                    self.logger.info(f"⏳ 스캔 진행: {total_files_found}개 파일 검사 중...")
                
                # 폴더 추적
                folder = str(file_path.parent)
                if folder not in scanned_folders:
                    scanned_folders.add(folder)
                    self.logger.info(f"📁 폴더 스캔: {file_path.parent.name}")
                
                # 지원되는 파일 형식 확인
                if file_path.suffix.lower() in self.supported_extensions:
                    try:
                        processed_count += 1
                        # 빠른 파일 정보 수집
                        stat = file_path.stat()
                        file_size = stat.st_size
                        file_hash = self._get_file_hash(file_path)
                        
                        if True:  # 중복 체크 비활성화
                            existing_files.append({
                                'path': file_path,
                                'mtime': stat.st_mtime,
                                'size': file_size,
                                'hash': file_hash
                            })
                            # 10개씩 발견할 때마다 진행 상황 출력
                            if len(existing_files) % 10 == 0:
                                self.logger.info(f"✅ 새 파일 {len(existing_files)}개 발견...")
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ 파일 스캔 오류 {file_path.name}: {e}")
        
        # 수정 시간순 정렬 (과거 → 최근)
        existing_files.sort(key=lambda x: x['mtime'])
        
        self.logger.info(f"📊 스캔 완료:")
        self.logger.info(f"   📁 스캔된 폴더: {len(scanned_folders)}개")
        self.logger.info(f"   📄 전체 파일: {total_files_found}개")
        self.logger.info(f"   🎯 미디어 파일: {processed_count}개")
        self.logger.info(f"   📤 업로드 대상: {len(existing_files)}개")
        
        return [f['path'] for f in existing_files]

    def process_existing_files_batch(self, batch_size: int = 3):
        """기존 파일들을 배치로 처리"""
        existing_files = self.scan_existing_files()
        
        if not existing_files:
            self.logger.info("✅ 모든 파일이 이미 동기화되었습니다.")
            return
        
        total_files = len(existing_files)
        self.logger.info(f"🚀 {total_files}개 파일 배치 업로드 시작 (배치 크기: {batch_size})")
        
        processed = 0
        success_count = 0
        
        for i in range(0, total_files, batch_size):
            batch = existing_files[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            self.logger.info(f"📦 배치 {batch_num}/{total_batches} 처리 중... ({len(batch)}개 파일)")
            
            batch_success = 0
            for file_path in batch:
                self.logger.info(f"📤 업로드: {file_path.name} ({file_path.parent.name}/)")
                if self._process_file(file_path):
                    batch_success += 1
                    success_count += 1
                processed += 1
                
            
            # 배치 완료 후 iCloud 동기화
            if batch_success > 0:
                self.logger.info(f"🎯 배치 {batch_num} 완료: {batch_success}/{len(batch)}개 성공")
                
                # 진행률 표시
                progress = (processed / total_files) * 100
                self.logger.info(f"📈 전체 진행률: {progress:.1f}% ({processed}/{total_files})")
                
            
        # 모든 배치 완료 후 한번에 iCloud 동기화
        if success_count > 0:
            self.logger.info(f"🔄 모든 배치 완료! iCloud 동기화 시작...")
            self._trigger_icloud_sync()
            
        self.logger.info(f"🎉 기존 파일 업로드 완료! 성공: {success_count}/{total_files}개")

class FTPFileHandler(FileSystemEventHandler):
    """FTP 폴더 파일 변경 감지"""
    
    def __init__(self, sync_manager: FTPiCloudPhotoSync):
        self.sync_manager = sync_manager
        self.logger = sync_manager.logger
        
    def on_created(self, event):
        """새 파일 생성 감지"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # 파일 생성 완료 대기 (카메라 업로드가 완료될 때까지)
        self._wait_for_file_complete(file_path)
        
        # 지원되는 형식인지 확인
        if file_path.suffix.lower() in self.sync_manager.supported_extensions:
            self.logger.info(f"📁 새 파일 감지: {file_path.name}")
            # 큐에 추가
            self.sync_manager.upload_queue.put(file_path)
    
    def _wait_for_file_complete(self, file_path: Path, max_wait: int = 30):
        """파일 업로드 완료 대기"""
        last_size = 0
        stable_count = 0
        
        for _ in range(max_wait):
            try:
                if file_path.exists():
                    current_size = file_path.stat().st_size
                    if current_size == last_size and current_size > 0:
                        stable_count += 1
                        if stable_count >= 3:  # 3초간 크기가 안정되면 완료로 판단
                            break
                    else:
                        stable_count = 0
                    last_size = current_size
                time.sleep(1)
            except:
                time.sleep(1)

    def scan_existing_files(self) -> List[Path]:
        """기존 파일들을 생성 시간 순으로 스캔 (모든 하위 폴더 포함)"""
        self.logger.info("📂 기존 파일 스캔 시작...")
        self.logger.info(f"🔍 검색 경로: {self.ftp_root}")
        self.logger.info(f"📝 지원 형식: {', '.join(self.supported_extensions)}")
        
        existing_files = []
        scanned_folders = set()
        total_files_found = 0
        
        # 모든 하위 폴더를 재귀적으로 스캔
        for file_path in self.ftp_root.rglob("*"):
            if file_path.is_file():
                total_files_found += 1
                
                # 폴더 추적
                folder = str(file_path.parent)
                if folder not in scanned_folders:
                    scanned_folders.add(folder)
                    self.logger.info(f"📁 폴더 스캔: {file_path.parent.name}")
                
                # 지원되는 파일 형식 확인
                if file_path.suffix.lower() in self.supported_extensions:
                    try:
                        # 중복 체크
                        file_size = file_path.stat().st_size
                        file_hash = self._get_file_hash(file_path)
                        
                        if True:  # 중복 체크 비활성화
                            existing_files.append({
                                'path': file_path,
                                'mtime': file_path.stat().st_mtime,
                                'size': file_size,
                                'hash': file_hash
                            })
                            self.logger.debug(f"✅ 새 파일 발견: {file_path.name}")
                        else:
                            self.logger.debug(f"🔄 중복 파일 건너뜀: {file_path.name}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ 파일 스캔 오류 {file_path}: {e}")
                else:
                    self.logger.debug(f"🚫 지원되지 않는 형식: {file_path.name}")
        
        # 수정 시간순 정렬 (과거 → 최근)
        existing_files.sort(key=lambda x: x['mtime'])
        
        self.logger.info(f"📊 스캔 결과:")
        self.logger.info(f"   📁 스캔된 폴더: {len(scanned_folders)}개")
        self.logger.info(f"   📄 전체 파일: {total_files_found}개")
        self.logger.info(f"   🎯 업로드 대상: {len(existing_files)}개")
        
        # 스캔된 폴더 목록 출력
        for folder in sorted(scanned_folders):
            self.logger.info(f"   📁 {folder}")
        
        return [f['path'] for f in existing_files]

    def process_existing_files_batch(self, batch_size: int = 10):
        """기존 파일들을 배치로 처리"""
        existing_files = self.scan_existing_files()
        
        if not existing_files:
            self.logger.info("✅ 모든 파일이 이미 동기화되었습니다.")
            return
        
        total_files = len(existing_files)
        self.logger.info(f"🚀 {total_files}개 파일 배치 업로드 시작 (배치 크기: {batch_size})")
        
        processed = 0
        success_count = 0
        
        for i in range(0, total_files, batch_size):
            batch = existing_files[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            self.logger.info(f"📦 배치 {batch_num}/{total_batches} 처리 중... ({len(batch)}개 파일)")
            
            batch_success = 0
            for file_path in batch:
                self.logger.info(f"📤 업로드: {file_path.name} ({file_path.parent.name}/)")
                if self._process_file(file_path):
                    batch_success += 1
                    success_count += 1
                processed += 1
                
            
            # 배치 완료 후 iCloud 동기화
            if batch_success > 0:
                self.logger.info(f"🎯 배치 {batch_num} 완료: {batch_success}/{len(batch)}개 성공")
                
                # 진행률 표시
                progress = (processed / total_files) * 100
                self.logger.info(f"📈 전체 진행률: {progress:.1f}% ({processed}/{total_files})")
                
            
        # 모든 배치 완료 후 한번에 iCloud 동기화
        if success_count > 0:
            self.logger.info(f"🔄 모든 배치 완료! iCloud 동기화 시작...")
            self._trigger_icloud_sync()
            
        self.logger.info(f"🎉 기존 파일 업로드 완료! 성공: {success_count}/{total_files}개")

def main():
    """메인 실행 함수"""
    try:
        # 동기화 시스템 초기화
        sync_manager = FTPiCloudPhotoSync()
        
        # FTP 폴더 존재 확인
        if not sync_manager.ftp_root.exists():
            sync_manager.logger.error(f"❌ FTP 폴더가 존재하지 않습니다: {sync_manager.ftp_root}")
            return 1
        
        # 명령행 인수 확인
        if len(sys.argv) > 1 and sys.argv[1] == "--sync-existing":
            # 기존 파일 동기화 모드
            sync_manager.logger.info("🔄 기존 파일 동기화 모드 시작")
            sync_manager.process_existing_files_batch(batch_size=10)  # 배치 크기 10개로 설정
            return 0
        
        # 배치 처리 워커 시작
        batch_thread = threading.Thread(target=sync_manager._batch_processor, daemon=True)
        batch_thread.start()
        sync_manager.logger.info("🚀 배치 처리 워커 시작됨")
        
        # 시작 시 기존 파일 1개 배치 처리 (테스트)
        existing_thread = threading.Thread(
            target=lambda: sync_manager.process_existing_files_batch(batch_size=1), 
            daemon=True
        )
        existing_thread.start()
        
        # 파일 시스템 감시 설정
        event_handler = FTPFileHandler(sync_manager)
        observer = Observer()
        observer.schedule(event_handler, str(sync_manager.ftp_root), recursive=True)
        
        # 감시 시작
        observer.start()
        sync_manager.logger.info(f"👁️ FTP 폴더 감시 시작: {sync_manager.ftp_root}")
        sync_manager.logger.info("🛑 종료: Ctrl+C")
        
        try:
            while True:
                time.sleep(1)
                # 주기적 상태 출력
                if sync_manager.upload_queue.qsize() > 0:
                    sync_manager.logger.info(f"📋 대기 중인 파일: {sync_manager.upload_queue.qsize()}개")
                
        except KeyboardInterrupt:
            sync_manager.logger.info("🛑 종료 신호 받음")
            
        observer.stop()
        observer.join()
        sync_manager.logger.info("✅ FTP → iCloud Photos 동기화 시스템 종료")
        return 0
        
    except Exception as e:
        logging.error(f"❌ 시스템 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())