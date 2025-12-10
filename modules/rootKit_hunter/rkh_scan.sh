#!/bin/bash

# Script: rkh_scan.sh
# Objetivo: Rodar rkhunter automaticamente e permitir leitura do relatório

LOGFILE="/var/log/rkhunter.log"

echo "[*] Iniciando scan do rkhunter sem interação..."
sudo rkhunter --check --sk

echo "[*] Ajustando permissões do arquivo de log..."
sudo chmod o+r "$LOGFILE"

echo "[*] Permissões ajustadas: agora você pode ler o relatório."
echo "-------------------------------------------"
echo "[*] Exibindo conteúdo do relatório:"
echo "-------------------------------------------"

cat "$LOGFILE"

