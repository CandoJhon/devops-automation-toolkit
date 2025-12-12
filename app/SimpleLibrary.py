#!/usr/bin/env python3
"""
Simple Library Management API
Propósito: Demostrar herramientas DevOps en contexto real
"""

from flask import Flask, jsonify, request
import logging
import random
import time
from datetime import datetime
import os

# logging configuration
log_dir = '/app/logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# database simulation with a simple list
# In a real application, this would be replaced with a proper database
books_db = [
    {"id": 1, "title": "The DevOps Handbook", "author": "Gene Kim", "available": True},
    {"id": 2, "title": "Site Reliability Engineering", "author": "Google", "available": True},
    {"id": 3, "title": "Accelerate", "author": "Nicole Forsgren", "available": False},
    {"id": 4, "title": "The Phoenix Project", "author": "Gene Kim", "available": True},
]

# Request counter for logging
request_count = 0

@app.before_request
def log_request():
    global request_count
    request_count += 1
    logger.info(f"Request #{request_count}: {request.method} {request.path} from {request.remote_addr}")

@app.route('/')
def home():
    """Root endpoint - basic information"""
    return jsonify({
        "service": "Library Management API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "books": "/api/books",
            "metrics": "/metrics"
        }
    })

@app.route('/health')
def health():
    """
    Health check endpoint
    Occasionally simulates issues (10% probability)
    to make monitoring scenarios more interesting
    """
    # simulate slow response (20% probability)
    if random.random() > 0.8:
        time.sleep(2)  # simulate slow response
    
    # simulate occasional failure (10% probability)
    if random.random() > 0.9:
        logger.warning("Health check failed - simulated degraded state")
        return jsonify({
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "message": "Database connection slow"
        }), 503
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "available",
        "database": "connected"
    }), 200

@app.route('/api/books', methods=['GET'])
def get_books():
    # Get all books
    logger.info(f"Fetching all books - Total: {len(books_db)}")
    return jsonify({
        "books": books_db,
        "total": len(books_db)
    })

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    #get books by id
    book = next((b for b in books_db if b['id'] == book_id), None)
    if book:
        logger.info(f"Book found: {book['title']}")
        return jsonify(book)
    logger.warning(f"Book not found: ID {book_id}")
    return jsonify({"error": "Book not found"}), 404

@app.route('/api/books', methods=['POST'])
def add_book():
    """Add new book to the library"""
    data = request.get_json()
    new_book = {
        "id": len(books_db) + 1,
        "title": data.get('title'),
        "author": data.get('author'),
        "available": True
    }
    books_db.append(new_book)
    logger.info(f"New book added: {new_book['title']} by {new_book['author']}")
    return jsonify(new_book), 201

@app.route('/metrics')
def metrics():
    """Métricas simples para monitoring"""
    return jsonify({
        "total_requests": request_count,
        "total_books": len(books_db),
        "available_books": sum(1 for b in books_db if b['available']),
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    logger.error(f"404 Error: {request.url}")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Library Management API...")
    app.run(host='0.0.0.0', port=8000, debug=False)

