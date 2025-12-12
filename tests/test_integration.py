import pytest
import requests
import time


BASE_URL = "http://localhost:8000/"

def is_api_running():

    """Helper to check if API is running"""
    try:
        response = requests.get(BASE_URL, timeout=2)
        return response.status_code == 200
    except:
        return False

@pytest.mark.skipif(not is_api_running(), reason="API don't running")
class TestAPIIntegration:
    """Tests integration for Library Management API"""
    
    def test_api_home_endpoint(self):

        """Test endpoint home"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "Library Management API"
    
    def test_api_health_endpoint(self):

        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        # Puede ser 200 o 503 (simula fallos)
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
    
    def test_api_books_endpoint(self):

        """Test books endpoint"""
        response = requests.get(f"{BASE_URL}/api/books")
        assert response.status_code == 200
        data = response.json()
        assert "books" in data
        assert "total" in data
        assert isinstance(data["books"], list)
    
    def test_api_metrics_endpoint(self):

        """Test metrics endpoint"""
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_books" in data
    
    def test_api_response_time(self):

        """check API response time is acceptable"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/health")
        elapsed = time.time() - start
        
        # Should respond in less than 1 second
        assert elapsed < 1.0
