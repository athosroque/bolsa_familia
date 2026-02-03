import os
import requests
import time
from datetime import datetime
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.db.connection import get_connection
import psycopg2

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Configuration
BASE_URL = "https://portaldatransparencia.gov.br/api-de-dados"
ENDPOINT = "/bolsa-familia-por-municipio"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortalTransparenciaPipeline/1.0)",
    "Accept": "application/json",
    # "CHAVE-API-PORTAL": os.getenv("API_KEY") # Add if you have one
}

def get_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def fetch_data(session, mes_ano, codigo_ibge, pagina=1):
    """Fetches data from the API with pagination and rate limiting."""
    url = f"{BASE_URL}{ENDPOINT}"
    params = {
        "mesAno": mes_ano,
        "codigoIbge": codigo_ibge,
        "pagina": pagina
    }
    
    try:
        logging.info(f"Fetching page {pagina} for {mes_ano}/{codigo_ibge}...")
        response = session.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        time.sleep(1) # Rate limiting: 1s pause
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {e}")
        return None

def save_raw_data(data, mes_ano, codigo_ibge, pagina):
    """
    Saves the full JSON response to Postgres raw_bolsa_familia table.
    Skips if data already exists for this page.
    """
    conn = get_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        query = """
            INSERT INTO raw_bolsa_familia 
            (reference_date, municipality_code, page_number, api_response)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (reference_date, municipality_code, page_number) 
            DO NOTHING
        """
        date_obj = datetime.strptime(mes_ano, "%Y%m").date()
        
        cur.execute(query, (date_obj, codigo_ibge, pagina, json.dumps(data)))
        rows_affected = cur.rowcount
        conn.commit()
        
        if rows_affected > 0:
            logging.info(f"✅ Saved page {pagina} ({len(data)} records).")
        else:
            logging.info(f"⚠️ Page {pagina} already exists. Skipped.")
            
        cur.close()
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    # Example usage: Fetch Sao Paulo (3550308) for Jan 2024
    MES_ANO = "202401"
    CODIGO_IBGE = "3550308" 
    
    logging.info("Starting ELT process (Resilient Mode)...")
    
    # Ensure DB schema is up to date
    from src.db.connection import init_db
    init_db()

    session = get_session()
    page = 1
    
    while True:
        data = fetch_data(session, MES_ANO, CODIGO_IBGE, page)
        
        if not data:
            logging.info("No data returned. Ending process.")
            break
            
        save_raw_data(data, MES_ANO, CODIGO_IBGE, page)
        
        # Checking for empty list usually means end of pagination
        if isinstance(data, list) and len(data) == 0:
            logging.info("Reached end of data (empty list).")
            break
            
        page += 1
        
        if page > 100: # Safety cap increased
            logging.info("Safety limit (100) reached.")
            break

if __name__ == "__main__":
    main()
