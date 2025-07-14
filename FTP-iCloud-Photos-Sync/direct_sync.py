#!/usr/bin/env python3
"""
직접 동기화 스크립트 - 중복 체크 없이 모든 파일 업로드
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ftp_icloud_photos_sync import FTPiCloudPhotoSync
from pathlib import Path

def direct_sync():
    print("🎯 직접 동기화 시작 (중복 체크 없음)")
    
    sync_manager = FTPiCloudPhotoSync()
    
    # 모든 파일 스캔 (중복 체크 없이)
    print("📂 파일 스캔 중...")
    all_files = []
    
    for file_path in Path("/Volumes/990 PRO 2TB/FTP").rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in sync_manager.supported_extensions:
            if file_path.exists() and file_path.stat().st_size > 0:
                all_files.append(file_path)
    
    # 시간순 정렬
    all_files.sort(key=lambda x: x.stat().st_mtime)
    
    print(f"📊 발견된 파일: {len(all_files)}개")
    
    # 1개씩 업로드 (최대 안정성)
    batch_size = 1
    total_files = len(all_files)
    success_count = 0
    
    for i in range(0, total_files, batch_size):
        batch = all_files[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_files + batch_size - 1) // batch_size
        
        print(f"📦 배치 {batch_num}/{total_batches}: {len(batch)}개 파일 업로드 중...")
        
        try:
            result = sync_manager._add_batch_to_photos_app(batch)
            if result > 0:
                success_count += result
                print(f"✅ 배치 {batch_num} 성공: {result}개")
            else:
                print(f"❌ 배치 {batch_num} 실패")
        except Exception as e:
            print(f"❌ 배치 {batch_num} 오류: {e}")
        
        # 진행률 표시
        progress = ((i + len(batch)) / total_files) * 100
        print(f"📈 진행률: {progress:.1f}% ({i + len(batch)}/{total_files})")
        
        # 파일 간 3초 대기 (Photos 앱 안정화)
        import time
        time.sleep(3)
    
    print(f"🎉 동기화 완료! 성공: {success_count}/{total_files}개")
    
    # 마지막에 iCloud 동기화
    if success_count > 0:
        print("🔄 iCloud 동기화 시작...")
        sync_manager._trigger_icloud_sync()
        print("✅ 동기화 완료!")

if __name__ == "__main__":
    direct_sync()