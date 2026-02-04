from postgres_mcp import get_connection
import json

def run_verify():
    conn = get_connection()
    if not conn:
        print("❌ Failed to connect to DB via MCP config.")
        return

    cur = conn.cursor()
    
    print("--- 🔍 Verifying Schema Organization ---")
    
    # Check Tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = [t[0] for t in cur.fetchall()]
    print(f"Tables Found: {tables}")
    
    expected_tables = ['dim_municipio', 'dim_programa', 'fact_pagamentos_municipio']
    missing = [t for t in expected_tables if t not in tables]
    
    if not missing:
        print("✅ All Star Schema tables are present.")
    else:
        print(f"❌ Missing tables: {missing}")

    # Check Columns for Fact Table
    print("\n--- 🔍 Checking Fact Table Columns ---")
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='fact_pagamentos_municipio';")
    columns = [c[0] for c in cur.fetchall()]
    print(f"Columns: {columns}")
    
    # Validate against JSON Sample Logic
    # JSON 'valor' -> 'valor_total'
    # JSON 'quantidadeBeneficiados' -> 'quantidade_beneficiados'
    if 'valor_total' in columns and 'quantidade_beneficiados' in columns:
        print("✅ Fact table maps correctly to JSON 'valor' and 'quantidadeBeneficiados'")
    
    conn.close()

if __name__ == "__main__":
    run_verify()
