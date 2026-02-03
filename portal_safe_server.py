import httpx
import asyncio
import time
import logging
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("portal-transparencia")

mcp = FastMCP("portal-transparencia-safe")

BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
API_KEY = os.getenv("API_KEY")

# --- CONFIGURAÇÕES DE PROTEÇÃO DA API ---
RATE_LIMIT_DELAY = 1.5 
MAX_RETRIES = 3
_cache = {}

class APIGuard:
    def __init__(self):
        self.last_request_time = 0
        self.lock = asyncio.Lock()

    async def wait_for_slot(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < RATE_LIMIT_DELAY:
                wait_time = RATE_LIMIT_DELAY - elapsed
                await asyncio.sleep(wait_time)
            self.last_request_time = time.time()

api_guard = APIGuard()

def get_bolsa_familia_endpoint(mes_ano_str: str) -> str:
    """Retorna o endpoint correto baseado no histórico do programa."""
    try:
        data = datetime.strptime(mes_ano_str, "%Y%m")
        if data < datetime(2021, 11, 1):
            return "/bolsa-familia-por-municipio"
        elif data < datetime(2023, 3, 1):
            return "/auxilio-brasil-por-municipio"
        else:
            return "/novo-bolsa-familia-por-municipio"
    except:
        return "/novo-bolsa-familia-por-municipio"

async def safe_request(endpoint: str, params: dict):
    if not API_KEY:
        return "Erro: API_KEY não configurada no ambiente."

    cache_key = f"{endpoint}:{str(params)}"
    if cache_key in _cache:
        logger.info(f"Cache hit: {endpoint}")
        return _cache[cache_key]

    headers = {"chave-api-dados": API_KEY, "Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        for attempt in range(MAX_RETRIES):
            await api_guard.wait_for_slot()
            try:
                url = f"{BASE_URL}{endpoint}"
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    _cache[cache_key] = data
                    return data
                elif response.status_code == 429:
                    wait_time = (attempt + 2) ** 2
                    logger.warning(f"Rate limited (429). Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return f"Erro na API ({response.status_code}): {response.text}"
            except Exception as e:
                logger.error(f"Erro na requisição: {e}")
                if attempt == MAX_RETRIES - 1:
                    return f"Erro de conexão: {str(e)}"
                await asyncio.sleep(2)
        
    return "Falha após múltiplas tentativas."

# --- FERRAMENTAS (TOOLS) ---

@mcp.tool()
async def consultar_bolsa_familia_municipio(mes_ano: str, codigo_ibge: str, pagina: int = 1):
    """
    Consulta pagamentos do Bolsa Família por município.
    Lida automaticamente com as mudanças de nome do programa (Bolsa Família vs Auxílio Brasil).
    mes_ano: AAAAMM (ex: 202401).
    codigo_ibge: 7 dígitos.
    """
    endpoint = get_bolsa_familia_endpoint(mes_ano)
    return await safe_request(endpoint, {
        "mesAno": mes_ano, "codigoIbge": codigo_ibge, "pagina": pagina
    })

@mcp.tool()
async def consultar_licitacoes(data_inicial: str, data_final: str, pagina: int = 1):
    """
    Consulta licitações por período.
    Datas: DD/MM/AAAA. Intervalo máximo sugerido: 30 dias.
    """
    return await safe_request("/licitacoes", {
        "dataInicial": data_inicial, "dataFinal": data_final, "pagina": pagina
    })

@mcp.tool()
async def consultar_contratos(data_inicial: str, data_final: str, pagina: int = 1):
    """
    Consulta contratos firmados por período.
    Datas: DD/MM/AAAA.
    """
    return await safe_request("/contratos", {
        "dataInicial": data_inicial, "dataFinal": data_final, "pagina": pagina
    })

@mcp.tool()
async def consultar_cpcc(data_inicial: str, data_final: str, pagina: int = 1):
    """
    Consulta gastos com Cartão de Pagamento de Defesa Civil (CPDC).
    Datas: DD/MM/AAAA.
    """
    return await safe_request("/cartoes", {
        "dataInicial": data_inicial, "dataFinal": data_final, "pagina": pagina
    })

@mcp.tool()
async def consultar_emendas_parlamentares(ano: int, pagina: int = 1):
    """Consulta emendas parlamentares por ano (ex: 2023)."""
    return await safe_request("/emendas", {"ano": ano, "pagina": pagina})

if __name__ == "__main__":
    mcp.run(transport='stdio')