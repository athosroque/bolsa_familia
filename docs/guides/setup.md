# Guia de Instalação e Execução

## Pré-requisitos
- Docker & Docker Compose instalados.
- Ambiente Linux (recomendado Umbrel).

## 🚀 Inicialização Rápida

Para subir todo o ambiente (Banco de Dados + Container ETL) e verificar a instalação:

```bash
sudo ./setup.sh
```

Este script irá:
1. Construir as imagens Docker.
2. Iniciar o PostgreSQL e o PGAdmin.
3. Aguardar o banco estar pronto.
4. Rodar testes de conexão.

## 🔧 Gerenciamento
### Comandos Úteis
*   **Apenas subir containers:** `sudo docker compose up -d`
*   **Ver logs do banco:** `sudo docker compose logs -f db`
*   **Parar tudo:** `sudo docker compose down`

### Acesso Remoto
*   **Portainer:** Se estiver no Umbrel, os containers aparecerão automaticamente no Portainer.
*   **PGAdmin (Interface SQL):**
    *   URL: `http://<IP-DO-UMBREL>:5050`
    *   Email: `admin@umbrel.com`
    *   Senha: `admin`

*   **Portainer (Monitoramento Avançado):**
    Adicionamos um Portainer dedicado para ver este projeto.
    *   URL: `http://umbrel.local:9001` (ou `http://<IP-DO-UMBREL>:9001`)
    *   No primeiro acesso, você precisará criar uma senha de admin.
    *   Selecione **"Get Started"** com o ambiente local (socket).

## 🐞 Solução de Problemas
Se houver erros de **autenticação no banco** ao rodar o setup (comum se você trocou a senha no `.env` mas já tinha um banco criado), rode:

```bash
sudo ./fix_initialization.sh
```
Isso apaga o volume antigo e recria do zero.
