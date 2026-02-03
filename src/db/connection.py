import os
import json
import psycopg2
from psycopg2.extras import Json

# Database connection parameters - in production use env vars
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "portal_transparencia"),
    "user": os.getenv("POSTGRES_USER", "umbrel"),
    "password": os.getenv("POSTGRES_PASSWORD", "umbrel_password_change_me"),
    "host": os.getenv("DB_HOST", "localhost"),
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
                    page_number INTEGER,
                    api_response JSONB,
                    UNIQUE(reference_date, municipality_code, page_number)
                );
            """)
            # Migration for existing tables (safe to run)
            try:
                cur.execute("ALTER TABLE raw_bolsa_familia ADD COLUMN IF NOT EXISTS page_number INTEGER;")
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_dedup ON raw_bolsa_familia (reference_date, municipality_code, page_number);")
                conn.commit()
            except Exception as e:
                print(f"Migration warning: {e}")
                conn.rollback()

            conn.commit()
            conn.commit()
            print("Database initialized successfully.")
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error initializing DB: {error}")
        finally:
            conn.close()

if __name__ == '__main__':
    init_db()
