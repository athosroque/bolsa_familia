# Guia de Segurança

## Gerenciamento de Segredos
Este projeto utiliza variáveis de ambiente para gerenciar credenciais sensíveis.

> **⚠️ NUNCA commite o arquivo `.env` no Git.**

### 1. Configuração Segura
O arquivo `.env` contém as senhas reais e é ignorado pelo Git (`.gitignore`).
Para configurar um novo ambiente:
1.  Copie o exemplo: `cp .env.example .env`
2.  Edite o `.env` com suas senhas reais.

### 2. Logs e Histórico
*   Evite imprimir segredos em logs de console (`print(password)`).
*   Se for compartilhar logs (`project_log.md`), verifique se não há senhas expostas (ex: em URLs ou mensagens de erro de conexão).

### 3. Rotação de Senhas
Se precisar trocar a senha do banco de dados:
1.  Pare os serviços: `docker compose down`
2.  Edite `.env` com a nova senha.
3.  **Atenção:** Como o Postgres salva a senha no volume `pgdata`, simplesmente mudar o `.env` não altera a senha do banco já criado. Você precisará rodar o `./fix_initialization.sh` para recriar o volume (perdendo os dados locais) OU alterar a senha manualmente via SQL.
