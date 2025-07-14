#!/usr/bin/env python3

import asyncio
import signal
import sys
from efficient_monitor import EfficientMonitor
from process_controller import ProcessController

class SmartEfficientMonitor:
    def __init__(self):
        self.efficient_monitor = EfficientMonitor()
        self.process_controller = ProcessController()
        self.running = False
    
    async def run_efficient_monitoring(self):
        """효율적인 스마트 모니터링"""
        print("⚡ 효율적 자동화 모니터링 시작!")
        print("🎛️ 노션 체크박스로 원격 제어")
        print("🚀 30초마다 안전한 업데이트")
        print("💾 캐시 기반 효율적 동작")
        print("📊 등록된 프로세스만 모니터링")
        print("종료: Ctrl+C")
        print("-" * 60)
        
        self.running = True
        
        while self.running:
            try:
                # 1단계: 노션 제어 설정 확인 및 프로세스 제어
                self.process_controller.control_processes()
                
                # 2단계: 효율적 상태 업데이트
                updated = self.efficient_monitor.batch_update_notion()
                
                print(f"🔄 업데이트 완료 ({updated}개) - 다음: 30초 후")
                print("-" * 60)
                
                # 30초 대기 (API 제한 고려)
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"❌ 오류: {e}")
                await asyncio.sleep(5)
        
        print("🛑 효율적 모니터링 종료")

def signal_handler(signum, frame):
    print("\n🛑 종료 신호 수신...")
    sys.exit(0)

if __name__ == "__main__":
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    monitor = SmartEfficientMonitor()
    try:
        asyncio.run(monitor.run_efficient_monitoring())
    except KeyboardInterrupt:
        print("👋 모니터링 종료")