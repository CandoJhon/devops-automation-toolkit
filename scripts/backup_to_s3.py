#!/usr/bin/env python3
"""
Backup to AWS S3
"""

import boto3
import os
import sys
import tarfile
from datetime import datetime
from pathlib import Path

def compress_directory(source_dir, output_filename):
    """
    compress directory into a tar.gz file
    
    Args:
        source_dir: Path of the directory to compress
        output_filename: Name of the output file
    
    Returns:
        Path of the compressed file
    """
    print(f"Compressing {source_dir}...")
    
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    
    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"✓ Compressed to {output_filename} ({size_mb:.2f} MB)")
    
    return output_filename

def upload_to_s3(file_path, bucket_name, s3_key=None):
    """
    Upload file to S3
    
    Args:
        file_path: Local path of the file
        bucket_name: Name of the S3 bucket
        s3_key: S3 key (optional, uses filename if not provided)
    
    Returns:
        success is true, false otherwise
    """
    if s3_key is None:
        s3_key = f"backups/{os.path.basename(file_path)}"
    
    try:
        print(f"Uploading to s3://{bucket_name}/{s3_key}...")
        
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket_name, s3_key)
        
        print(f"✓ Successfully uploaded to S3")
        print(f"  Location: s3://{bucket_name}/{s3_key}")
        
        return True
        
    except Exception as e:
        print(f"✗ Upload failed: {str(e)}")
        return False

def backup_app_logs(bucket_name):
    """
    specific backup for application logs
    """
    logs_dir = "../app/logs"
    
    if not os.path.exists(logs_dir):
        print(f"✗ Logs directory not found: {logs_dir}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"app_logs_backup_{timestamp}.tar.gz"
    
    # Compress
    compress_directory(logs_dir, backup_filename)
    
    # Upload to S3
    success = upload_to_s3(backup_filename, bucket_name)
    
    # Clean up local temporary file
    if success:
        os.remove(backup_filename)
        print(f"✓ Temporary file removed: {backup_filename}")
    
    return success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_to_s3.py <bucket_name>")
        print("  python backup_to_s3.py <source_dir> <bucket_name>")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Specific mode: backup of app logs
        bucket_name = sys.argv[1]
        backup_app_logs(bucket_name)
    else:
        # Generic mode: backup of any directory
        source_dir = sys.argv[1]
        bucket_name = sys.argv[2]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{os.path.basename(source_dir)}_{timestamp}.tar.gz"
        
        compress_directory(source_dir, backup_filename)
        upload_to_s3(backup_filename, bucket_name)
        
        os.remove(backup_filename)
        print(f"✓ Backup complete")