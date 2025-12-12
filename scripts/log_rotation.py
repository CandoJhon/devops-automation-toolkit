#!/usr/bin/env python3
"""
Log Rotation Script
compresses old log files and deletes very old compressed logs
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = "../app/logs"
MAX_LOG_AGE_DAYS = 7  # Compress logs older than 7 days
MAX_COMPRESSED_AGE_DAYS = 30  # Delete compressed logs older than 30 days

def get_file_age_days(file_path):
    """Get file age in days"""
    file_time = os.path.getmtime(file_path)
    age = datetime.now() - datetime.fromtimestamp(file_time)
    return age.days

def compress_log_file(log_file):
    """
    Compress log file with gzip
    
    Args:
        log_file: Path of the file to compress
    
    Returns:
        Path of the compressed file
    """
    compressed_file = f"{log_file}.gz"
    
    print(f"Compressing {log_file}...")
    
    with open(log_file, 'rb') as f_in:
        with gzip.open(compressed_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Eliminar archivo original
    os.remove(log_file)
    
    original_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
    compressed_size = os.path.getsize(compressed_file)
    
    print(f"✓ Compressed: {compressed_file}")
    print(f"  Size reduction: {original_size} → {compressed_size} bytes")
    
    return compressed_file

def rotate_logs():
    """Main log rotation process"""
    
    if not os.path.exists(LOG_DIR):
        print(f"✗ Log directory not found: {LOG_DIR}")
        return
    
    print(f"Starting log rotation in {LOG_DIR}...")
    print("=" * 60)
    
    # Action counters
    compressed_count = 0
    deleted_count = 0
    
    # Iterate over files in log directory
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        
        # Ignore directories
        if os.path.isdir(file_path):
            continue
        
        age_days = get_file_age_days(file_path)
        
        # Case 1: Uncompressed logs older than MAX_LOG_AGE_DAYS
        if filename.endswith('.log') and age_days > MAX_LOG_AGE_DAYS:
            compress_log_file(file_path)
            compressed_count += 1
        
        # Case 2: Compressed logs older than MAX_COMPRESSED_AGE_DAYS
        elif filename.endswith('.gz') and age_days > MAX_COMPRESSED_AGE_DAYS:
            print(f"Deleting old compressed log: {filename} (age: {age_days} days)")
            os.remove(file_path)
            deleted_count += 1
    
    # Summary
    print("=" * 60)
    print(f"Log rotation complete:")
    print(f"  Files compressed: {compressed_count}")
    print(f"  Files deleted: {deleted_count}")

if __name__ == "__main__":
    rotate_logs()