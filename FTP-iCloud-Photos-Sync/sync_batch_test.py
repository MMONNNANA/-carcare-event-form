#!/usr/bin/env python3
"""
배치 업로드 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ftp_icloud_photos_sync import FTPiCloudPhotoSync
from pathlib import Path

def test_batch_upload():
    print("🎯 배치 업로드 테스트 시작")
    
    sync_manager = FTPiCloudPhotoSync()
    
    # 테스트할 파일들 찾기
    test_files = []
    for file_path in Path("/Volumes/990 PRO 2TB/FTP/사진 백업").glob("*.heic"):
        if file_path.exists() and file_path.stat().st_size > 0:
            test_files.append(file_path)
            if len(test_files) >= 3:  # 3개만 테스트
                break
    
    if not test_files:
        print("❌ 테스트할 파일을 찾을 수 없습니다.")
        return
    
    print(f"📂 테스트 파일: {len(test_files)}개")
    for f in test_files:
        print(f"   - {f.name}")
    
    # 배치 업로드 실행
    result = sync_manager._add_batch_to_photos_app(test_files)
    
    if result > 0:
        print(f"✅ 배치 업로드 성공: {result}개 파일")
        # DB에 기록
        for file_path in test_files:
            stat = file_path.stat()
            file_size = stat.st_size
            file_hash = sync_manager._get_file_hash(file_path)
            sync_manager._record_upload(file_path, file_size, file_hash)
        print("📝 DB 기록 완료")
    else:
        print("❌ 배치 업로드 실패")

if __name__ == "__main__":
    test_batch_upload()