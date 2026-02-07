# 📊 Portal da Transparência - Data Pipeline & Analytics

## Visão Geral do Projeto

Este projeto implementa um **pipeline de dados (ETL/ELT) robusto e escalável** focado na extração, armazenamento e análise de dados do **Bolsa Família** e outros programas sociais brasileiros. A fonte primária dos dados é a API do Portal da Transparência do Governo Federal. O diferencial deste projeto reside na sua arquitetura local baseada em Docker, na modelagem dimensional para análises eficientes e na integração com **Agentes MCP (Model Context Protocol)**, permitindo que Large Language Models (LLMs) interajam diretamente com os dados.

O objetivo é fornecer uma solução completa para a ingestão e análise de dados governamentais, facilitando a obtenção de insights e a tomada de decisões baseada em dados.

## 🏗️ Arquitetura e Fluxo de Dados

O sistema é projetado para rodar inteiramente em um ambiente local containerizado com Docker e segue a arquitetura **ELT (Extract, Load, Transform)**, otimizada para análise de dados. A modelagem dimensional utiliza um **Star Schema** para garantir consultas rápidas e eficientes.

### Componentes Principais:

1.  **Ingestão (Extract)**:
    *   Scripts Python (`src/etl/`) são responsáveis por baixar dados da API do Portal da Transparência.
    *   Gerencia automaticamente a paginação, limites de taxa (rate limits) da API e autenticação.

2.  **Armazenamento (Load)**:
    *   Os dados brutos extraídos são armazenados em formato **JSONB** na tabela `raw_bolsa_familia` em um banco de dados **PostgreSQL 16**.
    *   Esta abordagem permite flexibilidade para esquemas semi-estruturados e facilita futuras transformações.

3.  **Transformação (Transform)**:
    *   Após o carregamento, os dados brutos são processados e transformados em um formato otimizado para análise.
    *   São criadas tabelas dimensionais para estruturar os dados:
        *   `fact_pagamentos_municipio` (Tabela Fato: Contém as métricas e chaves estrangeiras para as dimensões).
        *   `dim_municipio` (Tabela Dimensão: Detalhes sobre os municípios).
        *   `dim_programa` (Tabela Dimensão: Detalhes sobre os programas sociais).

## 🤖 Agentes MCP (Model Context Protocol)

Uma característica inovadora deste projeto é a inclusão de servidores **MCP (Model Context Protocol)**, que permitem a interação de LLMs (como Claude ou Gemini) com os dados e a API de forma segura e controlada. Isso abre portas para análises conversacionais e automação inteligente.

-   **`pg-aiguide`**: Este agente permite que LLMs consultem o banco de dados PostgreSQL. Ele pode listar tabelas, descrever esquemas e executar consultas SQL de forma controlada, facilitando a exploração de dados por meio de linguagem natural.
-   **`portal-safe`**: Um cliente de API seguro que permite que LLMs realizem consultas em tempo real à API do Portal da Transparência, garantindo que as interações com a API externa sejam gerenciadas de forma eficiente e segura.

## 🛠️ Stack Tecnológica

-   **Linguagem**: `Python`
-   **Orquestração**: `Docker` & `Docker Compose`
-   **Banco de Dados**: `PostgreSQL 16`
-   **Processamento de Dados**: `Pandas`
-   **Integração LLM**: `Model Context Protocol (MCP)`
-   **Ferramentas**: `API do Portal da Transparência`

## 🚀 Como Rodar o Projeto (Guia de Início Rápido)

Para configurar e executar o pipeline de dados localmente, siga as instruções abaixo:

### 1. Pré-requisitos

Certifique-se de ter os seguintes softwares instalados:

-   **Docker**
-   **Docker Compose**

Além disso, você precisará de uma chave de API do Portal da Transparência. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```dotenv
API_KEY=SUA_CHAVE_DE_API_AQUI
```

### 2. Iniciar os Serviços

Execute o script de configuração para construir as imagens Docker e iniciar os serviços:

```bash
./setup.sh
```

### 3. Executar a Carga de Dados (ETL)

#### Para baixar dados de um mês específico:

```bash
sudo docker compose exec etl python src/etl/extract_bolsa_familia.py --month YYYYMM
# Exemplo: sudo docker compose exec etl python src/etl/extract_bolsa_familia.py --month 202401
```

#### Para baixar dados de um ano inteiro (modo Batch):

```bash
sudo docker compose exec -d etl python src/etl/extract_bolsa_familia.py --year YYYY
# Exemplo: sudo docker compose exec -d etl python src/etl/extract_bolsa_familia.py --year 2024
```

### 4. Análise Exploratória de Dados (com Pandas)

Para interagir com os dados carregados em um shell Python com Pandas, execute:

```bash
sudo docker compose exec -it -e PYTHONPATH=/app etl python src/analysis/repl_session.py
```

## 📂 Estrutura de Arquivos

```text
├── .env                     # Variáveis de ambiente (API_KEY)
├── docker-compose.yml       # Definição dos serviços Docker
├── fix_initialization.sh    # Script para corrigir inicialização (se necessário)
├── host.json                # Configuração do Azure Function Host (se aplicável)
├── postgres_mcp.py          # Servidor MCP para PostgreSQL
├── portal_safe_server.py    # Servidor MCP para a API do Portal da Transparência
├── requirements.txt         # Dependências Python
├── sample_response.json     # Exemplo de resposta da API
├── setup.sh                 # Script de configuração e inicialização
├── tests/                   # Testes unitários e de integração
│   ├── inspect_api.py
│   └── verify_setup.py
└── src/                     # Código fonte principal
    ├── analysis/            # Scripts para análise de dados
    │   ├── repl_session.py  # Shell interativo com Pandas
    │   └── verify_pandas.py
    ├── db/                  # Conexão e esquema do banco de dados
    │   └── connection.py
    └── etl/                 # Scripts de Extração, Transformação e Carga
        ├── __init__.py
        └── extract_bolsa_familia.py
```

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues para sugestões ou melhorias, ou enviar Pull Requests.

---

Desenvolvido por **Athos Roque Barros**

[LinkedIn](https://www.linkedin.com/in/athos-roque-barros-622038152/)
[GitHub](https://github.com/athosroque)
