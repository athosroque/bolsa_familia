import os
import json
import psycopg2
from psycopg2.extras import Json

# Database connection parameters - in production use env vars
DB_CONFIG = {
    "dbname": "portal_transparencia",
    "user": "umbrel",
    "password": "umbrel_password_change_me",
    "host": os.getenv("DB_HOST", "localhost"), # Default to localhost, use 'db' in docker
    "port": "5432"
}

def get_connection():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to database: {error}")
        return None

def init_db():
    """Create tables if they don't exist"""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Create table for raw Bolsa Familia data
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_bolsa_familia (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    ingested_at TIMESTAMP DEFAULT NOW(),
                    reference_date DATE,
                    municipality_code TEXT,
                    api_response JSONB
                );
            """)
            conn.commit()
            print("Database initialized successfully.")
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error initializing DB: {error}")
        finally:
            conn.close()

if __name__ == '__main__':
    init_db()
