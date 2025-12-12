import sys
import os
import tempfile
import gzip
from datetime import datetime, timedelta
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.log_rotation import get_file_age_days, compress_log_file

def test_get_file_age_days():


    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        
    try:
        age = get_file_age_days(file_path)
        assert age >= 0
        assert isinstance(age, int)
        
    finally:
        os.remove(file_path)

def test_compress_log_file():

    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_file:
        temp_file.write("Log line 1\n")
        temp_file.write("Log line 2\n")
        temp_file.write("Log line 3\n")
        log_path = temp_file.name
    
    compressed_path = f"{log_path}.gz"
    
    try:
        result = compress_log_file(log_path)
        
        # assertions
        assert result == compressed_path
        assert os.path.exists(compressed_path)
        assert not os.path.exists(log_path)  # root file should be removed
        
        # assert compressed content
        with gzip.open(compressed_path, 'rt') as f:
            content = f.read()
            assert "Log line 1" in content
            assert "Log line 2" in content
            
    finally:
        if os.path.exists(compressed_path):
            os.remove(compressed_path)
        if os.path.exists(log_path):
            os.remove(log_path)

def test_compress_log_file_reduces_size():
    

    # create file with repetitive content to ensure good compression
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_file:
        for i in range(1000):
            temp_file.write("This is a repetitive log line\n")
        log_path = temp_file.name
    
    compressed_path = f"{log_path}.gz"
    original_size = os.path.getsize(log_path)
    
    try:
        compress_log_file(log_path)
        compressed_size = os.path.getsize(compressed_path)
        
        # compression should reduce file size significantly
        assert compressed_size < original_size
        assert compressed_size < original_size * 0.5  # at least 50% reduction
        
    finally:
        if os.path.exists(compressed_path):
            os.remove(compressed_path)