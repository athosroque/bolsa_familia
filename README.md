# Portal da Transparência - Data Pipeline & Analytics

Este projeto implementa um pipeline de dados (ETL) robusto para extrair, armazenar e analisar dados do **Bolsa Família** (e outros programas sociais) usando a API do Portal da Transparência do Governo Federal.

## 🏗 Arquitetura

O sistema roda inteiramente local em Docker e segue a arquitetura **ELT (Extract, Load, Transform)** com modelagem dimensional (**Star Schema**) para facilitar análises.

*   **Ingestão (Extract):** Scripts Python (`src/etl/`) baixam dados da API, tratando paginação, rate limits e autenticação.
*   **Armazenamento (Load):** Dados brutos são salvos em JSONB na tabela `raw_bolsa_familia` (PostgreSQL 16).
*   **Transformação (Transform):** Dados são processados e movidos para tabelas dimensionais:
    *   `fact_pagamentos_municipio` (Fato)
    *   `dim_municipio` (Dimensão)
    *   `dim_programa` (Dimensão)

## 🤖 Agentes MCP (Model Context Protocol)
O projeto inclui servidores MCP para permitir que LLMs (como Claude/Gemini) interajam com os dados:
1.  **pg-aiguide**: Permite consultar o banco de dados Postgres (listar tabelas, rodar SQL).
2.  **portal-safe**: Cliente de API seguro para consultas em tempo real.

## 🚀 Como Rodar

### 1. Pré-requisitos
*   Docker & Docker Compose
*   Arquivo `.env` com `API_KEY` do Portal da Transparência.

### 2. Iniciar Serviços
```bash
./setup.sh
```

### 3. Executar Carga de Dados
Para baixar dados de um mês específico:
```bash
sudo docker compose exec etl python src/etl/extract_bolsa_familia.py --month 202401
```

Para baixar o ano todo (Batch):
```bash
sudo docker compose exec -d etl python src/etl/extract_bolsa_familia.py --year 2024
```

### 4. Análise Exploratória (Pandas)
Para abrir um shell interativo com os dados carregados:
```bash
sudo docker compose exec -it -e PYTHONPATH=/app etl python src/analysis/repl_session.py
```

## 📂 Estrutura de Arquivos
*   `src/etl/`: Scripts de extração.
*   `src/db/`: Conexão e Schema do banco.
*   `src/analysis/`: Scripts para EDA e Pandas.
*   `postgres_mcp.py`: Servidor MCP para o banco.
*   `portal_safe_server.py`: Servidor MCP para a API.
