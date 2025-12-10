#!/usr/bin/env bash
# ShadowSec MalwareScan Module v1.0
# Maldet + ClamAV Scanner
# Autor: Luciano Valadão

# ==========================
#   CONFIGURAÇÕES INICIAIS
# ==========================

LOG_DIR="/var/log/shadowsec"
LAST_SCAN_FILE="$LOG_DIR/maldet_last_scan.txt"

mkdir -p "$LOG_DIR"

# Cores
RED="\e[31m"; GREEN="\e[32m"; YELLOW="\e[33m"; BLUE="\e[34m"; PINK="\e[35m"; END="\e[0m"

# Validar root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] Execute como root.${END}"
    exit 1
fi

# ==========================
#     FUNÇÕES GERAIS
# ==========================

update_definitions() {
    echo -e "${BLUE}[*] Atualizando ClamAV e Maldet...${END}"
    freshclam
    maldet --update-signatures
    echo -e "${GREEN}[OK] Assinaturas atualizadas.${END}"
    sleep 2
}

save_last_scan() {
    echo "$1" > "$LAST_SCAN_FILE"
}

view_last_report() {
    if [ ! -f "$LAST_SCAN_FILE" ]; then
        echo -e "${RED}[!] Nenhum relatório salvo.${END}"
        return
    fi
    SCANID=$(cat "$LAST_SCAN_FILE")
    maldet --report "$SCANID"
}

view_specific_report() {
    read -p "Digite o SCANID: " SCANID
    maldet --report "$SCANID"
}

list_reports() {
    echo -e "${BLUE}Relatórios disponíveis em /usr/local/maldetect/sessions:${END}"
    ls /usr/local/maldetect/sessions/
}

# ==========================
#     FUNÇÕES DE SCAN
# ==========================

scan_quick() {
    TARGETS="/home /tmp /var/tmp"
    echo -e "${YELLOW}[+] Scan rápido iniciado...${END}"
    run_scan "$TARGETS"
}

scan_recommended() {
    TARGETS="/home /usr /var /opt /root"
    echo -e "${GREEN}[+] Scan recomendado iniciado...${END}"
    run_scan "$TARGETS"
}

scan_deep() {
    TARGETS="/"
    IGNORE="--exclude-dir=/proc --exclude-dir=/sys --exclude-dir=/dev --exclude-dir=/run --exclude-dir=/mnt --exclude-dir=/media --exclude-dir=/snap"
    echo -e "${BLUE}[+] Scan profundo iniciado...${END}"
    run_scan "$TARGETS" "$IGNORE"
}

scan_aggressive() {
    echo -e "${RED}[!] Modo agressivo: extremamente lento e pesado.${END}"
    read -p "Deseja continuar? (s/n): " ans
    [ "$ans" != "s" ] && return
    TARGETS="/"
    run_scan "$TARGETS"
}

run_scan() {
    TARGETS="$1"
    EXTRA="$2"

    maldet --scan-all $TARGETS $EXTRA
    SCANID=$(grep -oP '\d{6}-\d{4}\.\d+' /usr/local/maldetect/event_log | tail -1)

    if [ -n "$SCANID" ]; then
        save_last_scan "$SCANID"
        echo -e "${GREEN}[OK] Scan concluído. SCANID: $SCANID${END}"
        echo -e "Para ver o relatório depois: maldet --report $SCANID"
    else
        echo -e "${RED}[!] Falha ao detectar SCANID.${END}"
    fi
}

# ==========================
#   AGENDAMENTO DE SCANS
# ==========================

schedule_scan() {
    echo -e "\n${BLUE}Configurar agendamento:${END}"
    echo "1) Diário"
    echo "2) Semanal"
    echo "3) Mensal"
    echo "4) Personalizado"
    read -p "Escolha: " opt

    case $opt in
        1)
            CRONLINE="0 3 * * * root /usr/local/shadowsec/shadowsec_maldet.sh --recommended"
            ;;
        2)
            CRONLINE="0 4 * * 1 root /usr/local/shadowsec/shadowsec_maldet.sh --recommended"
            ;;
        3)
            CRONLINE="0 4 1 * * root /usr/local/shadowsec/shadowsec_maldet.sh --recommended"
            ;;
        4)
            read -p "Minutos: " m
            read -p "Hora: " h
            read -p "Dia do mês (* para qualquer): " dom
            read -p "Mês (*): " mon
            read -p "Dia da semana (0-6/*): " dow
            CRONLINE="$m $h $dom $mon $dow root /usr/local/shadowsec/shadowsec_maldet.sh --recommended"
            ;;
        *)
            echo -e "${RED}[!] Opção inválida.${END}"
            return
            ;;
    esac

    echo "# SHADOWSEC-MALDET" >> /etc/crontab
    echo "$CRONLINE" >> /etc/crontab

    echo -e "${GREEN}[OK] Agendamento configurado.${END}"
}

show_schedules() {
    echo -e "${BLUE}Agendamentos ativos:${END}"
    grep SHADOWSEC-MALDET -n /etc/crontab || echo "Nenhum agendamento."
}

remove_schedules() {
    sed -i '/SHADOWSEC-MALDET/d' /etc/crontab
    echo -e "${GREEN}[OK] Agendamentos removidos.${END}"
}

# ==========================
#          MENU
# ==========================

main_menu() {
while true; do
    clear
    echo -e "${PINK}ShadowSec Malware Scanner – Maldet Module${END}"
    echo "============================================"
    echo "1) Scan rápido"
    echo "2) Scan recomendado"
    echo "3) Scan profundo"
    echo "4) Scan agressivo"
    echo "5) Ver último relatório"
    echo "6) Ver relatório específico"
    echo "7) Listar relatórios"
    echo "8) Atualizar definições"
    echo "9) Agendar scan"
    echo "10) Ver agendamentos"
    echo "11) Remover agendamentos"
    echo "0) Sair"
    echo
    read -p "Escolha: " opt

    case $opt in
        1) scan_quick ;;
        2) scan_recommended ;;
        3) scan_deep ;;
        4) scan_aggressive ;;
        5) view_last_report ;;
        6) view_specific_report ;;
        7) list_reports ;;
        8) update_definitions ;;
        9) schedule_scan ;;
        10) show_schedules ;;
        11) remove_schedules ;;
        0) exit ;;
        *) echo -e "${RED}Opção inválida.${END}" ;;
    esac
    read -p "Pressione ENTER para continuar..."
done
}

main_menu

