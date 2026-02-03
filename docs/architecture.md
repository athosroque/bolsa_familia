# Arquitetura Técnica

## 🛠 Tech Stack & Infraestrutura
- **OS:** Linux (Umbrel Home Lab) - Focado em rodar em hardware doméstico de baixo consumo.
- **Runtime:** Docker & Docker Compose.
- **Banco de Dados:** **PostgreSQL 16**

### Decisões de Design
*   **PostgreSQL Puro:** Substituiu a ideia inicial de usar Supabase self-hosted para economizar recursos do hardware (CPU/RAM).
*   **Armazenamento JSONB:** Utilizamos a coluna `api_response` do tipo JSONB para salvar a resposta exata da API. Isso permite mudar a estratégia de extração de dados no futuro sem precisar baixar tudo de novo.

## 🏗 Fluxo de Dados (ELT)
Adotamos uma abordagem **ELT** (Extract, Load, Transform) em vez de ETL tradicional.

1.  **Extract:** Scripts Python (`src/etl/`) consultam a API `portaldatransparencia.gov.br`.
2.  **Load:** O JSON original da resposta é salvo *intacto* na tabela `raw_bolsa_familia` (Postgres). Nenhuma perda de dados.
3.  **Transform (Futuro):** Views SQL ou Pandas/dbt serão usados para limpar e estruturar dados tabularmente apenas quando uma pergunta de negócio ou modelo de ML for definido.

## 📂 Estrutura do Repositório
```text
/home/umbrel/portal-transparencia/
├── docs/                   # Documentação do projeto
├── src/                    # Código fonte Python
│   ├── etl/                # Scripts de extração
│   └── db/                 # Gerenciamento de conexão
├── tests/                  # Testes unitários e de integração
├── pgdata/                 # Volume persistente do Postgres (não versionado)
├── docker-compose.yml      # Orquestração dos containers
└── setup.sh                # Script de inicialização
```
