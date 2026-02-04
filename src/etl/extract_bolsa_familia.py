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
        if 'response' in locals() and response:
            logging.error(f"Response content: {response.text[:200]}")
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
            logging.info(f"⚠️ Page {pagina} already exists. Skipped RAW insert.")
            
        cur.close()
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def process_and_load(data):
    """
    Parses the JSON data and loads it into the relational Star Schema.
    """
    conn = get_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        
        # Ensure data is a list
        items = data if isinstance(data, list) else [data]
        
        for item in items:
            # 1. Upsert Dimension: Municipio
            mun = item.get("municipio", {})
            uf = mun.get("uf", {})
            cur.execute("""
                INSERT INTO dim_municipio (codigo_ibge, nome_ibge, uf_sigla, nome_regiao, pais)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (codigo_ibge) DO UPDATE SET
                    nome_ibge = EXCLUDED.nome_ibge,
                    uf_sigla = EXCLUDED.uf_sigla,
                    nome_regiao = EXCLUDED.nome_regiao;
            """, (
                mun.get("codigoIBGE"),
                mun.get("nomeIBGE"),
                uf.get("sigla"),
                mun.get("nomeRegiao"),
                mun.get("pais")
            ))

            # 2. Upsert Dimension: Programa
            prog = item.get("tipo", {})
            cur.execute("""
                INSERT INTO dim_programa (id, descricao, descricao_detalhada)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    descricao = EXCLUDED.descricao,
                    descricao_detalhada = EXCLUDED.descricao_detalhada;
            """, (
                prog.get("id"),
                prog.get("descricao"),
                prog.get("descricaoDetalhada")
            ))

            # 3. Insert Fact: Pagamentos
            cur.execute("""
                INSERT INTO fact_pagamentos_municipio 
                (data_referencia, codigo_ibge, programa_id, valor_total, quantidade_beneficiados)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (data_referencia, codigo_ibge, programa_id) DO UPDATE SET
                    valor_total = EXCLUDED.valor_total,
                    quantidade_beneficiados = EXCLUDED.quantidade_beneficiados;
            """, (
                item.get("dataReferencia"),
                mun.get("codigoIBGE"),
                prog.get("id"),
                item.get("valor"),
                item.get("quantidadeBeneficiados")
            ))
            
        conn.commit()
        logging.info(f"🔄 Processed {len(items)} records into Relational Schema.")
        cur.close()
    except Exception as e:
        logging.error(f"Relational processing failed: {e}")
        conn.rollback()
    finally:
        conn.close()

import argparse

def run_month(mes_ano, codigo_ibge):
    logging.info(f"🚀 Starting processing for {mes_ano}...")
    
    # Ensure DB schema is up to date
    init_db()

    endpoint = get_endpoint_by_date(mes_ano)
    session = get_session()
    page = 1
    
    while True:
        data = fetch_data(session, endpoint, mes_ano, codigo_ibge, page)
        
        if not data:
            logging.info(f"🏁 Finished {mes_ano}. End of data or error.")
            break
            
        # 1. Load Raw (Bronze)
        save_raw_data(data, mes_ano, codigo_ibge, page)
        
        # 2. Process to Relational (Silver/Gold)
        process_and_load(data)
        
        # Pagination check
        if isinstance(data, list) and len(data) == 0:
            break
            
        if not isinstance(data, list) or len(data) < 10: 
             break

        page += 1
        if page > 500: # Safety cap
            logging.warning("Safety limit reached (500 pages).")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Portal Transparencia ETL')
    parser.add_argument('--year', type=int, help='Process entire year (YYYY)')
    parser.add_argument('--month', type=str, help='Process specific month (YYYYMM)')
    parser.add_argument('--ibge', type=str, default="3550308", help='IBGE Code (default: SP)')
    
    args = parser.parse_args()
    
    if args.year:
        logging.info(f"📅 Batch processing for Year {args.year}")
        for m in range(1, 13):
            mes_ano = f"{args.year}{m:02d}"
            run_month(mes_ano, args.ibge)
            time.sleep(2) # Cooldown between months
    elif args.month:
        run_month(args.month, args.ibge)
    else:
        # Default behavior (Test)
        run_month("202401", args.ibge)
