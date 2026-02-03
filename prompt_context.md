# Contexto do Projeto: Pipeline Portal da Transparência (Umbrel)

> **Resumo para Prompts:** Copie este bloco para dar contexto rápido a outros agentes ou chats.

## 📌 Sobre o Projeto
**Nome:** Portal da Transparência Data Pipeline
**Objetivo:** Coletar dados públicos do governo brasileiro (foco inicial em **Bolsa Família**) para análise local e Machine Learning futuro.
**Filosofia:** "À prova de futuro" (ELT) - Armazenar dados brutos primeiro, modelar depois.

## 🛠 Tech Stack & Infraestrutura
- **OS:** Linux (Umbrel Home Lab)
- **Banco de Dados:** **PostgreSQL 16** (Container Docker Puro)
  - *Obs:* Substituiu a ideia inicial do Supabase completo para economizar recursos.
- **Linguagem ETL:** **Python 3.x**
- **Orquestração:** Cronjobs locais ou Loops em Python (inicialmente).
- **Armazenamento:** JSONB (coluna `api_response`) para flexibilidade de schema.

## 🏗 Arquitetura de Dados (ELT)
1.  **Extract:** Scripts Python consultam a API `portaldatransparencia.gov.br`.
2.  **Load:** JSON original da resposta é salvo *intacto* na tabela `raw_bolsa_familia` (Postgres).
3.  **Transform (Futuro):** Views SQL ou Pandas para limpar e estruturar dados para ML quando o objetivo for definido.

## 📂 Estrutura de Diretórios
```
/home/umbrel/portal-transparencia/
├── docker-compose.yml      # Banco de dados Postgres
├── context.md              # Este arquivo
├── src/
│   ├── etl/                # Scripts de extração
│   └── db/                 # Gerenciamento de conexão
└── data/                   # (Opcional) Arquivos temporários
```

## 🎯 Status Atual
- [x] Arquitetura definida (Local/Postgres).
- [ ] Ambiente Docker configurado.
- [ ] Primeiro script de coleta (Bolsa Família) em desenvolvimento.
