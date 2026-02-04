import pandas as pd
from src.db.connection import get_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def load_data():
    conn = get_connection()
    if not conn:
        print("❌ Connection failed")
        return None
    
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
        print("📊 Loading data into Pandas DataFrame...")
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        print("\n✅ Data Loaded Successfully!")
        print(f"Shape: {df.shape}")
        
        print("\n--- First 5 Rows ---")
        print(df.head())
        
        print("\n--- Basic Statistics (Valor) ---")
        # Converting Decimal to float for describe if needed, likely handled by read_sql
        print(df['valor_total'].astype(float).describe())

        print("\n--- Total Transacted (2024) ---")
        total = df['valor_total'].sum()
        print(f"R$ {total:,.2f}")
