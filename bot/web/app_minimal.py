"""Minimal Flask app for testing"""
from flask import Flask, jsonify
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting minimal Flask app...")

BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"TEMPLATE_DIR exists: {TEMPLATE_DIR.exists()}")
logger.info(f"STATIC_DIR exists: {STATIC_DIR.exists()}")

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

logger.info(f"✅ Flask app created")
logger.info(f"   template_folder: {app.template_folder}")
logger.info(f"   static_folder: {app.static_folder}")


@app.route('/')
def index():
    logger.info("GET / called")
    return jsonify({'status': 'ok', 'message': 'Flask is running from minimal app'})


@app.route('/health')
def health():
    logger.info("GET /health called")
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
