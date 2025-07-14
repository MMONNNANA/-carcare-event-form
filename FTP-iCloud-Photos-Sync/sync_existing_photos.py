#!/usr/bin/env python3
"""
기존 FTP 사진 일괄 동기화 스크립트
과거부터 최근 순으로 모든 사진을 Photos 앱으로 동기화
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ftp_icloud_photos_sync import FTPiCloudPhotoSync

def main():
    """기존 사진 일괄 동기화"""
    print("🎯 FTP 기존 사진 일괄 동기화 시작")
    print("📅 과거 → 최근 순으로 업로드")
    print("=" * 50)
    
    sync_manager = FTPiCloudPhotoSync()
    
    # FTP 폴더 존재 확인
    if not sync_manager.ftp_root.exists():
        print(f"❌ FTP 폴더가 존재하지 않습니다: {sync_manager.ftp_root}")
        return 1
    
    try:
        # 기존 파일들을 배치 처리
        sync_manager.process_existing_files_batch(batch_size=3)  # 안전하게 3개씩
        print("\n🎉 모든 기존 사진 동기화 완료!")
        
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
        return 1
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())