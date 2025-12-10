#!/bin/bash

# ShadowSec Toolkit - system_checkup.sh
# Autor: Luciano Valadão
# Descrição: Verificação de atualizações, limpeza, antivírus, firewall, pacotes órfãos e backups

clear
echo "====================================="
echo " ShadowSec Toolkit - System Checkup  "
echo "====================================="

# 1. Atualizações do sistema
echo -e "\n[1] Verificando atualizações do sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Limpando pacotes desnecessários
echo -e "\n[2] Limpando pacotes desnecessários..."
sudo apt autoremove -y
sudo apt autoclean -y

# 3. Remoção de pacotes órfãos
echo -e "\n[3] Removendo pacotes órfãos com deborphan..."
sudo deborphan | xargs -r sudo apt -y remove --purge

# 4. Verificação com ClamAV
echo -e "\n[4] Verificando sistema com ClamAV..."
sudo freshclam
sudo clamscan -r --bell -i /home

# 5. Verificando status do firewall
echo -e "\n[5] Verificando status do firewall (ufw)..."
sudo ufw status verbose

# 6. Backup simples da pasta pessoal
echo -e "\n[6] Criando backup da pasta pessoal..."
BACKUP_DIR="$HOME/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r $HOME/Documents $BACKUP_DIR 2>/dev/null
cp -r $HOME/Pictures $BACKUP_DIR 2>/dev/null
cp -r $HOME/Desktop $BACKUP_DIR 2>/dev/null
echo "Backup salvo em: $BACKUP_DIR"

# Fim
echo -e "\n✅ Verificação concluída."
echo "Você pode revisar os resultados acima."
exit 0

