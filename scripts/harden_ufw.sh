#!/bin/bash
# ========================================================
#  Shadows Cyber Defense - Firewall Hardening (UFW)
#  Versão interativa com opções de configuração
# ========================================================

# -------------------------------------------
# Verificação de privilégios
# -------------------------------------------
if [[ $EUID -ne 0 ]]; then
    echo "[!] Este script deve ser executado como root ou com sudo."
    exec sudo bash "$0" "$@"
    exit $?
fi

# -------------------------------------------
# Cabeçalho
# -------------------------------------------
echo -e "\n🛡️  Shadows Cyber Defense - UFW Hardening"
echo "--------------------------------------------"

# -------------------------------------------
# Backup das regras existentes
# -------------------------------------------
BACKUP_FILE=~/ufw_backup_$(date +%F_%H-%M-%S).txt
echo "[+] Fazendo backup das regras atuais em: $BACKUP_FILE"
ufw status numbered > "$BACKUP_FILE" 2>/dev/null || echo "[i] Nenhuma regra anterior detectada."

# -------------------------------------------
# Reset de regras (confirmação)
# -------------------------------------------
read -p "[?] Deseja resetar todas as regras atuais do UFW? (y/N): " RESET
if [[ "$RESET" =~ ^[Yy]$ ]]; then
    echo "[+] Resetando regras..."
    ufw --force reset
else
    echo "[i] Mantendo regras existentes."
fi

# -------------------------------------------
# Definir políticas padrão
# -------------------------------------------
echo "[+] Configurando políticas padrão..."
read -p "[?] Política de entrada (deny/allow): " POLICY_IN
read -p "[?] Política de saída (allow/deny): " POLICY_OUT

ufw default ${POLICY_IN:-deny} incoming
ufw default ${POLICY_OUT:-allow} outgoing

# -------------------------------------------
# Permitir SSH
# -------------------------------------------
read -p "[?] Deseja permitir acesso SSH? (y/N): " SSH_OK
if [[ "$SSH_OK" =~ ^[Yy]$ ]]; then
    read -p "   -> Porta SSH (padrão 22): " SSH_PORT
    SSH_PORT=${SSH_PORT:-22}
    echo "[+] Permitindo SSH na porta $SSH_PORT..."
    ufw allow ${SSH_PORT}/tcp
fi

# -------------------------------------------
# Permitir HTTP/HTTPS
# -------------------------------------------
read -p "[?] Deseja liberar HTTP/HTTPS (para servidor web)? (y/N): " WEB_OK
if [[ "$WEB_OK" =~ ^[Yy]$ ]]; then
    echo "[+] Permitindo portas 80 e 443..."
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

# -------------------------------------------
# Regras adicionais
# -------------------------------------------
while true; do
    read -p "[?] Deseja adicionar uma regra manual (porta/protocolo)? (y/N): " ADD_RULE
    if [[ "$ADD_RULE" =~ ^[Yy]$ ]]; then
        read -p "   -> Porta (ex: 8080): " PORT
        read -p "   -> Protocolo (tcp/udp): " PROTO
        ufw allow ${PORT}/${PROTO}
        echo "[+] Regra adicionada: ${PORT}/${PROTO}"
    else
        break
    fi
done

# -------------------------------------------
# Logging
# -------------------------------------------
read -p "[?] Deseja habilitar logs do UFW? (y/N): " LOG_OK
if [[ "$LOG_OK" =~ ^[Yy]$ ]]; then
    echo "[+] Ativando logs..."
    ufw logging on
else
    ufw logging off
fi

# -------------------------------------------
# Ativação final
# -------------------------------------------
echo "[+] Ativando firewall..."
ufw --force enable

# -------------------------------------------
# Exibir resultado
# -------------------------------------------
echo "[+] Configuração final do UFW:"
ufw status verbose

echo -e "\n✅ Firewall configurado com sucesso, meu Shadows."
echo "   Backup salvo em: $BACKUP_FILE"

