#!/usr/bin/env python3
"""
Health Check Monitor
monitoring script for web services and registering results
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration
ENDPOINTS = [
    {
        "name": "Library API - Home",
        "url": "http://library-api:8000/",
        "expected_status": 200,
        "timeout": 5
    },
    {
        "name": "Library API - Health",
        "url": "http://library-api:8000/health",
        "expected_status": 200,
        "timeout": 5
    },
    {
        "name": "Library API - Books",
        "url": "http://library-api:8000/api/books",
        "expected_status": 200,
        "timeout": 5
    }
]

LOG_FILE = "health_check.log"

def log_message(message, level="INFO"):
    """register log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + '\n')

def check_endpoint(endpoint):
    """
    Check availability of an endpoint
    Returns: dictionary with check result
    """
    try:
        start_time = time.time()
        response = requests.get(
            endpoint['url'], 
            timeout=endpoint['timeout']
        )
        response_time = round((time.time() - start_time) * 1000, 2)  # ms
        
        status_ok = response.status_code == endpoint['expected_status']
        
        result = {
            "name": endpoint['name'],
            "url": endpoint['url'],
            "status_code": response.status_code,
            "expected_status": endpoint['expected_status'],
            "response_time_ms": response_time,
            "success": status_ok,
            "timestamp": datetime.now().isoformat()
        }
        
        if status_ok:
            log_message(
                f"✓ {endpoint['name']} - Status: {response.status_code} - "
                f"Response time: {response_time}ms",
                "INFO"
            )
        else:
            log_message(
                f"✗ {endpoint['name']} - Expected {endpoint['expected_status']}, "
                f"got {response.status_code}",
                "WARNING"
            )
        
        return result
        
    except requests.exceptions.Timeout:
        log_message(f"✗ {endpoint['name']} - Timeout after {endpoint['timeout']}s", "ERROR")
        return {
            "name": endpoint['name'],
            "url": endpoint['url'],
            "success": False,
            "error": "Timeout",
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.ConnectionError:
        log_message(f"✗ {endpoint['name']} - Connection refused", "ERROR")
        return {
            "name": endpoint['name'],
            "url": endpoint['url'],
            "success": False,
            "error": "Connection refused",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_message(f"✗ {endpoint['name']} - Error: {str(e)}", "ERROR")
        return {
            "name": endpoint['name'],
            "url": endpoint['url'],
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_health_checks():
    """Run health checks on all endpoints"""
    log_message("=" * 60)
    log_message("Starting health checks...")
    
    results = []
    for endpoint in ENDPOINTS:
        result = check_endpoint(endpoint)
        results.append(result)
        time.sleep(1)  # Small pause between checks
    
    # Summary
    total = len(results)
    successful = sum(1 for r in results if r.get('success', False))
    failed = total - successful
    
    log_message("-" * 60)
    log_message(f"Summary: {successful}/{total} checks passed, {failed} failed")
    log_message("=" * 60)
    
    return results

def continuous_monitoring(interval=60):
    """
    Continuous monitoring
    Args:
        interval: seconds between each check
    """
    log_message(f"Starting continuous monitoring (interval: {interval}s)")
    log_message("Press Ctrl+C to stop")
    
    try:
        while True:
            run_health_checks()
            time.sleep(interval)
    except KeyboardInterrupt:
        log_message("Monitoring stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":

        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        continuous_monitoring(interval)
        
    else:
        run_health_checks()