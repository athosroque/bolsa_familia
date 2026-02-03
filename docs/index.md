# Portal da Transparência Data Pipeline

## 📌 Sobre o Projeto
**Objetivo:** Coletar dados públicos do governo brasileiro (foco inicial em **Bolsa Família**) para análise local e Machine Learning futuro.

**Filosofia:** "À prova de futuro" (ELT) - Armazenar dados brutos primeiro, modelar depois.
Os dados são extraídos da API do Portal da Transparência e armazenados em formato bruto (JSONB) no PostgreSQL para máxima flexibilidade.

## 🎯 Status Atual
- [x] Arquitetura definida (Local/Postgres).
- [x] Ambiente Docker configurado (Docker Compose).
- [x] Script de setup automatizado (`setup.sh`).
- [ ] Primeiro script de coleta (Bolsa Família) em desenvolvimento.

## 📚 Navegação
- [Arquitetura Técnica](architecture.md)
- [Guia de Instalação](guides/setup.md)
- [Logs de Execução](logs/project_log.md)
