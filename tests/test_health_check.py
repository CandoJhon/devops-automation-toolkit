import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.health_check import check_endpoint, ENDPOINTS

@patch('scripts.health_check.requests.get')
def test_check_endpoint_success(mock_get):

    """endpoint test successful"""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    endpoint = {
        "name": "Test API",
        "url": "http://test.com/api",
        "expected_status": 200,
        "timeout": 5
    }
    
    result = check_endpoint(endpoint)
    
    assert result["success"] == True
    assert result["status_code"] == 200
    assert "response_time_ms" in result
    assert result["name"] == "Test API"

@patch('scripts.health_check.requests.get')
def test_check_endpoint_wrong_status(mock_get):
    """endpoint test wrong status code"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response
    endpoint = {
        "name": "Test Error",
        "url": "http://test.com/error",
        "expected_status": 200,
        "timeout": 5
    }
    
    result = check_endpoint(endpoint)
    
    assert result["success"] == False
    assert result["status_code"] == 500

@patch('scripts.health_check.requests.get')
def test_check_endpoint_timeout(mock_get):
    """Test endpoint con timeout"""

    import requests
    mock_get.side_effect = requests.exceptions.Timeout()
    endpoint = {
        "name": "Slow Endpoint",
        "url": "http://test.com/slow",
        "expected_status": 200,
        "timeout": 1
    }
    
    result = check_endpoint(endpoint)
    
    assert result["success"] == False
    assert "error" in result
    assert result["error"] == "Timeout"


@patch('scripts.health_check.requests.get')
def test_check_endpoint_connection_error(mock_get):
    """endpoint test connection error"""
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    endpoint = {
        "name": "Invalid",
        "url": "http://invalid.test",
        "expected_status": 200,
        "timeout": 2
    }
    
    result = check_endpoint(endpoint)
    
    assert result["success"] == False
    assert "error" in result

def test_endpoints_configuration():
    """checks the ENDPOINTS configuration"""
    assert len(ENDPOINTS) > 0
    
    for endpoint in ENDPOINTS:
        assert "name" in endpoint
        assert "url" in endpoint
        assert "expected_status" in endpoint
        assert "timeout" in endpoint
        assert endpoint["url"].startswith("http")