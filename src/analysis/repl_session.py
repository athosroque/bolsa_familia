import pandas as pd
from src.db.connection import get_connection
import code
import logging
import warnings

# Suppress warnings for cleaner startup
warnings.filterwarnings('ignore')

def start_repl():
    print("⏳ Connecting to Database and loading data...")
    conn = get_connection()
    if not conn:
        print("❌ Connection failed")
        return
    
    query = """
    SELECT 
        f.data_referencia,
        m.nome_ibge as cidade,
        m.uf_sigla as uf,
        p.descricao as programa,
        f.valor_total,
        f.quantidade_beneficiados
    FROM fact_pagamentos_municipio f
    JOIN dim_municipio m ON f.codigo_ibge = m.codigo_ibge
    JOIN dim_programa p ON f.programa_id = p.id
    ORDER BY f.data_referencia;
    """
    
    try:
        df = pd.read_sql(query, conn)
        print(f"✅ Data loaded! DataFrame available as variable 'df'.")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print("\nType your pandas commands below (e.g., df.head(), df.describe())")
        print("Press Ctrl+D to exit.")
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        conn.close()

    # Start Interactive Shell
    code.interact(local=locals())

if __name__ == "__main__":
    start_repl()
