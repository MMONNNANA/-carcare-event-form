#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from src.main_monitor import ClaudeNotionMonitor
import asyncio

if __name__ == "__main__":
    print("🚀 Claude Code Notion Monitor 시작!")
    print("종료하려면 Ctrl+C를 눌러주세요.")
    print("-" * 50)
    
    try:
        asyncio.run(ClaudeNotionMonitor().start_monitoring())
    except KeyboardInterrupt:
        print("\n👋 모니터링을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")