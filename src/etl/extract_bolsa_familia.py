import os
import requests
import pandas as pd
from datetime import datetime
import json
import logging
from src.db.connection import get_connection

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Constants
BASE_URL = "https://portaldatransparencia.gov.br/api-de-dados"
ENDPOINT = "/bolsa-familia-por-municipio"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PortalTransparenciaPipeline/1.0)",
    "Accept": "application/json"
}

def fetch_data(mes_ano, codigo_ibge, pagina=1):
    """
    Fetches data from the API with pagination.
    Args:
        mes_ano (str): YYYYMM format (e.g., '202401')
        codigo_ibge (str): IBGE code for the municipality (e.g., '3550308' for Sao Paulo)
        pagina (int): Page number
    """
    url = f"{BASE_URL}{ENDPOINT}"
    params = {
        "mesAno": mes_ano,
        "codigoIbge": codigo_ibge,
        "pagina": pagina
    }
    
    try:
        logging.info(f"Fetching {url} with params {params}")
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {e}")
        return None

def save_raw_data(data, mes_ano, codigo_ibge):
    """
    Saves the full JSON response to Postgres raw_bolsa_familia table.
    """
    conn = get_connection()
    if not conn:
        logging.error("Database connection failed. Skipping save.")
        return

    try:
        cur = conn.cursor()
        query = """
            INSERT INTO raw_bolsa_familia (reference_date, municipality_code, api_response)
            VALUES (%s, %s, %s)
        """
        # Convert YYYYMM to Date object (1st day of month)
        date_obj = datetime.strptime(mes_ano, "%Y%m").date()
        
        # Insert generic JSON dump
        cur.execute(query, (date_obj, codigo_ibge, json.dumps(data)))
        conn.commit()
        logging.info(f"Saved {len(data) if isinstance(data, list) else 1} records to database.")
        cur.close()
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")
    finally:
        conn.close()

def main():
    # Example usage: Fetch Sao Paulo (3550308) for Jan 2024
    MES_ANO = "202401"
    CODIGO_IBGE = "3550308" 
    
    logging.info("Starting ELT process...")
    
    # Init DB (failsafe if not run before)
    # from src.db.connection import init_db
    # init_db()

    page = 1
    while True:
        data = fetch_data(MES_ANO, CODIGO_IBGE, page)
        
        if not data:
            logging.info("No more data or error occurred.")
            break
            
        save_raw_data(data, MES_ANO, CODIGO_IBGE)
        
        # Check if we should continue (API specific logic needed here)
        # For this specific endpoint, let's assume if we get < 15 items it's the end?
        # Or simple pagination check.
        if isinstance(data, list) and len(data) == 0:
            break
            
        page += 1
        # Safety break for testing
        if page > 5: 
            logging.info("Safety limit reached (5 pages). Stopping.")
            break

if __name__ == "__main__":
    main()
