import os
import requests
import time
from datetime import datetime
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.db.connection import get_connection, init_db

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Configuration
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortalTransparenciaPipeline/1.0)",
    "Accept": "application/json",
    "chave-api-dados": API_KEY
}

def get_endpoint_by_date(mes_ano_str):
    """
    Retorna o endpoint correto baseado na data de referência:
    - Até 10/2021: Bolsa Família
    - 11/2021 a 02/2023: Auxílio Brasil
    - 03/2023 em diante: Novo Bolsa Família
    """
    try:
        data = datetime.strptime(mes_ano_str, "%Y%m")
        if data < datetime(2021, 11, 1):
            return "/bolsa-familia-por-municipio"
        elif data < datetime(2023, 3, 1):
            return "/auxilio-brasil-por-municipio"
        else:
            return "/novo-bolsa-familia-por-municipio"
    except Exception as e:
        logging.error(f"Erro ao parsear data {mes_ano_str}: {e}")
        return "/novo-bolsa-familia-por-municipio"

def get_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def fetch_data(session, endpoint, mes_ano, codigo_ibge, pagina=1):
    """Fetches data from the API with pagination and rate limiting."""
    url = f"{BASE_URL}{endpoint}"
    params = {
        "mesAno": mes_ano,
        "codigoIbge": codigo_ibge,
        "pagina": pagina
    }
    
    try:
        logging.info(f"Fetching page {pagina} from {endpoint} for {mes_ano}/{codigo_ibge}...")
        response = session.get(url, headers=HEADERS, params=params, timeout=30)
        
        if response.status_code == 429:
             logging.warning("Rate limit hit. Waiting 10s...")
             time.sleep(10)
             return fetch_data(session, endpoint, mes_ano, codigo_ibge, pagina)
             
        response.raise_for_status()
        time.sleep(1.5) # Rate limiting: 1.5s pause as per docs safety
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {e}")
        return None

def save_raw_data(data, mes_ano, codigo_ibge, pagina):
    """
    Saves the full JSON response to Postgres raw_bolsa_familia table.
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
        
        # Se data for uma lista (muitos beneficiários por página) ou um objeto único
        cur.execute(query, (date_obj, codigo_ibge, pagina, json.dumps(data)))
        rows_affected = cur.rowcount
        conn.commit()
        
        if rows_affected > 0:
            logging.info(f"✅ Saved page {pagina} ({len(data) if isinstance(data, list) else 1} records).")
        else:
            logging.info(f"⚠️ Page {pagina} already exists. Skipped.")
            
        cur.close()
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def main(mes_ano="202401", codigo_ibge="3550308"):
    if not API_KEY:
        logging.error("API_KEY not found. Please set it in .env file.")
        return

    logging.info(f"Starting ELT process for {mes_ano} in {codigo_ibge}...")
    
    # Ensure DB schema is up to date
    init_db()

    endpoint = get_endpoint_by_date(mes_ano)
    session = get_session()
    page = 1
    
    while True:
        data = fetch_data(session, endpoint, mes_ano, codigo_ibge, page)
        
        if not data:
            logging.info("End of data or error. Finishing.")
            break
            
        save_raw_data(data, mes_ano, codigo_ibge, page)
        
        # Pagination check
        if isinstance(data, list) and len(data) == 0:
            break
            
        # If it's the 'por-municipio' endpoint, it usually returns a single summary object or a very small list
        if not isinstance(data, list) or len(data) < 10: # Assuming page size is larger
             break

        page += 1
        if page > 500: # Safety cap
            break

if __name__ == "__main__":
    # You can change these for manual tests
    import sys
    target_date = sys.argv[1] if len(sys.argv) > 1 else "202401"
    target_city = sys.argv[2] if len(sys.argv) > 2 else "3550308"
    main(target_date, target_city)
