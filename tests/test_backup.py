import sys
import os
import tempfile
import tarfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.backup_to_s3 import compress_directory

def test_compress_directory_creates_file():


    with tempfile.TemporaryDirectory() as temp_dir:

        # create test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # compress directory
        output_file = "test_backup.tar.gz"
        
        try:
            result = compress_directory(temp_dir, output_file)
            
            # assertions
            assert os.path.exists(output_file)
            assert result == output_file
            assert os.path.getsize(output_file) > 0
            
            # assert valid tar file
            assert tarfile.is_tarfile(output_file)
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.remove(output_file)

def test_compress_directory_with_multiple_files():

    
    with tempfile.TemporaryDirectory() as temp_dir:

        # create multiple test files
        for i in range(5):
            file_path = os.path.join(temp_dir, f"file_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"content {i}")
        
        output_file = "test_multi.tar.gz"
        
        try:
            compress_directory(temp_dir, output_file)
            
            # check tar contents
            with tarfile.open(output_file, 'r:gz') as tar:
                members = tar.getmembers()
                assert len(members) >= 5
                
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

def test_compress_empty_directory():
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = "test_empty.tar.gz"
        
        try:
            compress_directory(temp_dir, output_file)
            assert os.path.exists(output_file)
            
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)