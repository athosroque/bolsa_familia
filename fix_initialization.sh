#!/bin/bash
set -e

LOG_FILE="docs/logs/project_log.md"
echo "" >> $LOG_FILE
echo "## Execução do Script de Correção - $(date)" >> $LOG_FILE

echo "🔧 Parando containers e removendo volume antigo..." | tee -a $LOG_FILE
sudo docker compose down
sudo rm -rf pgdata
echo "✅ Volume removido." | tee -a $LOG_FILE

echo "🚀 Reiniciando setup..." | tee -a $LOG_FILE

# Run setup (which builds and starts containers)
if sudo ./setup.sh >> $LOG_FILE 2>&1; then
    echo "✅ Setup concluído com sucesso!" | tee -a $LOG_FILE
    echo "Status: 🟢 Sucesso" >> $LOG_FILE
else
    echo "❌ Setup falhou novamente. Verifique os logs acima em $LOG_FILE." | tee -a $LOG_FILE
    echo "Status: 🔴 Falha Recorrente" >> $LOG_FILE
    
    echo "🔍 Logs do Banco de Dados:" >> $LOG_FILE
    sudo docker compose logs db | tail -n 20 >> $LOG_FILE
fi
