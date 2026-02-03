import requests
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
HEADERS = {
    "Accept": "application/json",
    "chave-api-dados": os.getenv("API_KEY")
}

def get_endpoint_by_date(mes_ano_str):
    """
    Retorna o endpoint correto baseado na data de referência:
    - Até 10/2021: Bolsa Família
    - 11/2021 a 02/2023: Auxílio Brasil
    - 03/2023 em diante: Novo Bolsa Família
    """
    data = datetime.strptime(mes_ano_str, "%Y%m")
    
    if data < datetime(2021, 11, 1):
        return "/bolsa-familia-por-municipio"
    elif data < datetime(2023, 3, 1):
        return "/auxilio-brasil-por-municipio"
    else:
        return "/novo-bolsa-familia-por-municipio"

def main():
    if not HEADERS["chave-api-dados"]:
        logging.error("ERRO: API_KEY não encontrada no arquivo .env!")
        return

    # Amostras para validar as três fases do programa
    test_dates = ["202101", "202206", "202401"]
    ibge_sp = "3550308"
    
    print("\n" + "="*60)
    print("INSPEÇÃO MULTI-PROGRAMA (Portal da Transparência)")
    print("="*60)

    for mes_ano in test_dates:
        endpoint = get_endpoint_by_date(mes_ano)
        url = f"{BASE_URL}{endpoint}"
        params = {"mesAno": mes_ano, "codigoIbge": ibge_sp, "pagina": 1}
        
        logging.info(f"Inspecionando {mes_ano} via {endpoint}...")
        
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data:
                    print(f"\n✅ DATA: {mes_ano} | ENDPOINT: {endpoint}")
                    print(json.dumps(data[0] if isinstance(data, list) else data, indent=2, ensure_ascii=False))
                else:
                    logging.warning(f"Nenhum dado retornado para {mes_ano}")
            else:
                logging.error(f"Erro {r.status_code}: {r.text}")
        except Exception as e:
            logging.error(f"Falha na requisição: {e}")

    print("\n" + "="*60)
    print("Dica: Use o endpoint '/novo-bolsa-familia-por-municipio' para dados de 2024.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
