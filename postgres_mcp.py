#!/usr/bin/env python3
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastmcp import FastMCP
import json
from dotenv import load_dotenv

load_dotenv() # Load .env file

# Initialize FastMCP
mcp = FastMCP("pg-aiguide")

# Database Configuration (reads from env or defaults to local docker)
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "portal_transparencia"),
    "user": os.getenv("POSTGRES_USER", "umbrel"),
    "password": os.getenv("POSTGRES_PASSWORD", "umbrel_password_change_me"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": "5432"
}

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"DEBUG: Connection failed: {e}")
        return None

@mcp.tool()
def list_tables():
    """List all tables in the public schema."""
    conn = get_connection()
    if not conn:
        return "Error: Could not connect to database."
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = [row[0] for row in cur.fetchall()]
        return tables
    finally:
        conn.close()

@mcp.tool()
def describe_table(table_name: str):
    """Get the schema definition for a specific table."""
    conn = get_connection()
    if not conn:
        return "Error: Could not connect to database."
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}';
        """)
        columns = cur.fetchall()
        return json.dumps(columns, indent=2)
    except Exception as e:
        return f"Error describing table: {str(e)}"
    finally:
        conn.close()

@mcp.tool()
def run_read_only_query(query: str):
    """
    Run a READ-ONLY SQL query. 
    WARNING: Only SELECT statements are allowed.
    """
    if not query.strip().lower().startswith("select"):
        return "Error: Only SELECT statements are allowed for safety."
        
    conn = get_connection()
    if not conn:
        return "Error: Could not connect to database."
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        results = cur.fetchall()
        # Serialize to JSON to handle dates/decimals
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"Query Error: {str(e)}"
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run(transport='stdio')
