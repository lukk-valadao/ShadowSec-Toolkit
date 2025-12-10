#!/bin/bash

# Script para configurar suspensão automática após 15 minutos de inatividade
# Ideal para ambientes corporativos
# Ver equivalente em modules/idle_suspend_check.py
# Por: Shadows + Aeris Satana 🦇

CONF_FILE="/etc/systemd/logind.conf"
BACKUP_FILE="/etc/systemd/logind.conf.bkp-$(date +%Y%m%d-%H%M%S)"

# Verifica se está sendo executado como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script precisa ser executado como root. Use: sudo $0"
   exit 1
fi

echo "🔧 Iniciando configuração de suspensão automática..."

# Backup
cp "$CONF_FILE" "$BACKUP_FILE"
echo "📦 Backup criado em: $BACKUP_FILE"

# Ajusta as configurações
sed -i 's/^#*IdleAction=.*/IdleAction=suspend/' "$CONF_FILE"
sed -i 's/^#*IdleActionSec=.*/IdleActionSec=15min/' "$CONF_FILE"

# Se as opções não existirem, adiciona ao final
grep -q '^IdleAction=' "$CONF_FILE" || echo 'IdleAction=suspend' >> "$CONF_FILE"
grep -q '^IdleActionSec=' "$CONF_FILE" || echo 'IdleActionSec=15min' >> "$CONF_FILE"

# Reinicia o serviço para aplicar
systemctl restart systemd-logind

echo "✅ Configuração aplicada: sistema suspenderá após 15 minutos de inatividade."
