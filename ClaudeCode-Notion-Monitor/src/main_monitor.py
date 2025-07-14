#!/usr/bin/env python3

import asyncio
import signal
import sys
from pathlib import Path
from claude_monitor import ClaudeActivityMonitor, setup_file_monitoring
from notion_client import NotionMonitor
import time
import logging

class ClaudeNotionMonitor:
    def __init__(self):
        self.claude_monitor = ClaudeActivityMonitor()
        self.notion_monitor = NotionMonitor()
        self.file_observer = None
        self.running = False
        self.notion_page_id = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def start_monitoring(self):
        """모니터링 시작"""
        self.logger.info("🚀 Claude Code Notion Monitor 시작")
        
        # 세션 추적 시작
        session_data = self.claude_monitor.start_session_tracking()
        
        # 노션에 초기 엔트리 생성
        response = self.notion_monitor.create_session_entry(session_data)
        if response:
            self.notion_page_id = response['id']
            self.logger.info(f"✅ 노션 페이지 생성: {self.notion_page_id}")
        
        # 파일 모니터링 시작
        self.file_observer = setup_file_monitoring(self.claude_monitor)
        
        self.running = True
        self.logger.info("📊 실시간 모니터링 활성화")
        
        # 주기적 업데이트 루프
        await self.monitoring_loop()
    
    async def monitoring_loop(self):
        """메인 모니터링 루프"""
        update_interval = 30  # 30초마다 업데이트
        
        while self.running:
            try:
                # 현재 세션 데이터 가져오기
                current_session = self.claude_monitor.get_current_session_data()
                
                if current_session and self.notion_page_id:
                    # 노션 업데이트
                    update_data = {
                        'duration': current_session.get('duration', 0),
                        'commands_count': current_session.get('commands_count', 0),
                        'status': current_session.get('status', 'Active')
                    }
                    
                    self.notion_monitor.update_session_entry(self.notion_page_id, update_data)
                    
                    # 로컬 데이터 저장
                    self.claude_monitor.save_session_data()
                    
                    self.logger.info(f"📈 세션 업데이트 - 명령어: {current_session.get('commands_count')}, "
                                   f"지속시간: {current_session.get('duration', 0):.1f}초")
                
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                self.logger.error(f"❌ 모니터링 루프 오류: {e}")
                await asyncio.sleep(5)
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.logger.info("🛑 모니터링 중지 중...")
        
        self.running = False
        
        # 파일 모니터링 중지
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        # 세션 종료
        self.claude_monitor.end_session()
        
        # 최종 노션 업데이트
        if self.notion_page_id:
            current_session = self.claude_monitor.get_current_session_data()
            if current_session:
                final_update = {
                    'duration': current_session.get('duration', 0),
                    'commands_count': current_session.get('commands_count', 0),
                    'status': 'Completed'
                }
                self.notion_monitor.update_session_entry(self.notion_page_id, final_update)
        
        # 최종 데이터 저장
        self.claude_monitor.save_session_data()
        
        self.logger.info("✅ 모니터링 완전 중지")

def signal_handler(signum, frame, monitor):
    """시그널 핸들러"""
    print("\n🛑 종료 신호 수신...")
    monitor.stop_monitoring()
    sys.exit(0)

async def main():
    """메인 함수"""
    monitor = ClaudeNotionMonitor()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, monitor))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, monitor))
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
    except Exception as e:
        monitor.logger.error(f"❌ 치명적 오류: {e}")
        monitor.stop_monitoring()
    finally:
        print("👋 Claude Code Notion Monitor 종료")

if __name__ == "__main__":
    asyncio.run(main())