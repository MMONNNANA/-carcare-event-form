#!/usr/bin/env python3

import sys
import os
import time
import asyncio
sys.path.append(os.path.dirname(__file__))

from automation_monitor import AutomationMonitor
from process_controller import ProcessController

class SmartMonitor:
    def __init__(self):
        self.automation_monitor = AutomationMonitor()
        self.process_controller = ProcessController()
    
    async def run_smart_monitoring(self):
        """스마트 모니터링 실행 (제어 + 모니터링)"""
        print("🧠 스마트 자동화 모니터링 시작!")
        print("🎛️ 노션에서 체크박스로 프로세스를 제어할 수 있습니다")
        print("🔄 10초마다 자동 업데이트")
        print("종료하려면 Ctrl+C를 눌러주세요.")
        print("-" * 60)
        
        while True:
            try:
                # 1단계: 노션 설정에 따라 프로세스 제어
                self.process_controller.control_processes()
                
                # 잠시 대기 (프로세스 시작 완료 대기)
                await asyncio.sleep(3)
                
                # 2단계: 현재 상태 모니터링 및 노션 업데이트
                self.automation_monitor.run_scan()
                
                print(f"✅ 모니터링 완료 - 다음 업데이트: 10초 후")
                print("-" * 60)
                
                # 10초 대기
                await asyncio.sleep(10)
                
            except KeyboardInterrupt:
                print("\n🛑 모니터링 중지...")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                await asyncio.sleep(10)
        
        print("👋 스마트 모니터링 종료")

if __name__ == "__main__":
    monitor = SmartMonitor()
    asyncio.run(monitor.run_smart_monitoring())