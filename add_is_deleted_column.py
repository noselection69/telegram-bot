#!/usr/bin/env python3
"""Migration: Add is_deleted column to cars table"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

db_url = os.getenv('DATABASE_URL', '')
if not db_url:
    logger.info('DATABASE_URL not set, skipping migration')
    sys.exit(0)

try:
    from sqlalchemy import create_engine, text
    
    # Convert async URL to sync
    sync_url = db_url.replace('+asyncpg://', '+psycopg2://')
    if '+psycopg2' not in sync_url:
        sync_url = sync_url.replace('postgresql://', 'postgresql+psycopg2://')
    
    logger.info('Connecting to database...')
    engine = create_engine(sync_url, echo=False)
    
    with engine.begin() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'cars' AND column_name = 'is_deleted'
        """))
        
        if result.fetchone():
            logger.info('Column is_deleted already exists')
        else:
            logger.info('Adding is_deleted column to cars table...')
            conn.execute(text('ALTER TABLE cars ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE'))
            logger.info('SUCCESS: Column added')
            
except Exception as e:
    logger.error(f'Migration error: {e}')

sys.exit(0)
