#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ShadowSec Network Diagnostic Tool v1.0 - Multi-Platform
# Autor: Luciano Valadão / 2025.
# Descrição: Diagnostica conflitos de IP em redes locais, detectando automaticamente o SO (Linux, Windows, macOS)
# Funcionalidades: Detecção de hosts, conflitos de IP, renovação automática de IP e relatório com timestamp

import subprocess                  # Executa comandos do sistema operacional (ex: ipconfig, nmap, arp-scan)
import re                          # Expressões regulares para extrair informações de textos (ex: IPs e MACs)
import os                          # Interage com o sistema operacional (ex: verificar privilégios)
import json                        # Salva o relatório em formato JSON legível
import datetime                    # Gera data/hora para timestamp nos arquivos
import platform                    # Detecta o sistema operacional atual (Linux, Windows, Darwin/macOS)
from collections import defaultdict  # Dicionário que cria listas automaticamente (útil para agrupar MACs por IP)

# ==================== CORES PARA O TERMINAL (estilo dark cyberpunk) ====================
RESET = "\033[0m"                  # Reseta a cor do terminal para o padrão
VIOLET = "\033[38;2;170;50;220m"   # Cor violeta profunda
BLOOD_RED = "\033[38;2;200;0;50m"  # Vermelho sangue (para alertas)
MIDNIGHT = "\033[38;2;0;50;150m"   # Azul noite (para mensagens positivas)
CYAN = "\033[38;2;0;180;200m"      # Ciano gelado (para informações gerais)

# Detecta o sistema operacional uma única vez (Linux, Windows ou Darwin = macOS)
OS = platform.system()

# ==================== FUNÇÃO AUXILIAR PARA EXECUTAR COMANDOS ====================
def run_command(cmd, capture_output=True, shell=True):
    """
    Executa um comando no terminal e retorna a saída.
    - capture_output=True: captura o texto de saída
    - shell=True: permite comandos complexos (com pipes, &&, etc.)
    """
    try:
        # Executa o comando e captura resultado
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=capture_output, text=True)
        # Se pediu captura, retorna apenas o texto de saída limpo
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        # Em caso de erro (comando falhou), avisa em vermelho
        print(f"{BLOOD_RED}[!] Erro ao executar comando: {e}{RESET}")
        return None

# ==================== OBTÉM IP E MAC DA MÁQUINA LOCAL ====================
def get_local_info():
    """Retorna o IP e MAC address da máquina atual, adaptado ao SO"""
    if OS == "Linux":
        # Linux: pega IP via rota padrão
        ip = run_command("ip route get 1 | awk '{print $7}'")
        # Pega MAC da primeira interface com ether (ajuste se necessário)
        mac = run_command("ip link | grep ether | head -1 | awk '{print $2}'")
    elif OS == "Windows":
        # Windows: busca linha com "Endereço IPv4"
        ip_line = run_command("ipconfig | findstr /i \"IPv4\"")
        ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', ip_line).group(1) if ip_line else "Unknown"
        # Pega MAC via comando getmac
        mac_line = run_command("getmac /fo csv /nh")
        mac = mac_line.split(',')[1].strip('"') if mac_line else "Unknown"
    elif OS == "Darwin":  # macOS
        # macOS: tenta interface en0 (Wi-Fi) ou en1
        ip = run_command("ipconfig getifaddr en0 || ipconfig getifaddr en1")
        mac_line = run_command("ifconfig en0 | grep ether || ifconfig en1 | grep ether")
        mac = re.search(r'ether (\S+)', mac_line).group(1) if mac_line else "Unknown"
    else:
        ip = mac = "Unknown"  # SO não suportado
    return ip or "Unknown", mac or "Unknown"

# ==================== DETECTA A SUB-REDE LOCAL (ex: 192.168.1.0/24) ====================
def get_local_network():
    """Descobre a sub-rede da rede atual baseada no gateway padrão"""
    if OS == "Linux":
        output = run_command("ip route | grep default")
        match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', output)
    elif OS == "Windows":
        output = run_command("ipconfig")
        match = re.search(r'Gateway.*: (\d+\.\d+\.\d+\.\d+)', output)
    elif OS == "Darwin":
        output = run_command("netstat -rn | grep default")
        match = re.search(r'default\s+(\d+\.\d+\.\d+\.\d+)', output)
    else:
        return None

    if match:
        ip = match.group(1)
        # Transforma o IP do gateway/src em sub-rede /24 (padrão mais comum)
        return f"{'.'.join(ip.split('.')[:-1])}.0/24"
    return None

# ==================== ESCANEIA HOSTS ATIVOS COM NMAP ====================
def scan_for_hosts(network):
    """Faz um ping scan com nmap para descobrir dispositivos ativos na rede"""
    print(f"{VIOLET}[+] Escaneando hosts em {network}...{RESET}")
    output = run_command(f"nmap -sn {network}")
    if not output:
        print(f"{BLOOD_RED}[!] nmap não encontrado ou falhou. Instale para melhor resultado.{RESET}")
        return []

    hosts = []
    current_ip = None
    for line in output.splitlines():
        # Procura por linhas com IP
        ip_match = re.search(r'Nmap scan report for .*?(\d+\.\d+\.\d+\.\d+)', line)
        if ip_match:
            current_ip = ip_match.group(1)
        # Procura por MAC e fabricante
        mac_match = re.search(r'MAC Address: (\S+) \((.+)\)', line)
        if current_ip and mac_match:
            hosts.append((current_ip, mac_match.group(1)))
            current_ip = None
        elif current_ip:
            # Se achou IP mas não MAC
            hosts.append((current_ip, "MAC Unknown"))
            current_ip = None
    return hosts

# ==================== VERIFICA CONFLITOS DE IP VIA TABELA ARP ====================
def check_ip_conflicts(network):
    """Compara tabela ARP para ver se algum IP está associado a mais de um MAC"""
    print(f"{VIOLET}[+] Verificando conflitos de IP...{RESET}")
    if OS == "Linux":
        output = run_command(f"arp-scan {network}")
    else:
        output = run_command("arp -a")  # Windows e macOS usam arp -a

    if not output:
        return {}

    ip_mac = defaultdict(list)  # Dicionário que cria listas automaticamente
    for line in output.splitlines():
        # Expressão regular flexível para capturar IP e MAC em vários formatos
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f:-]+)', line, re.IGNORECASE)
        if match:
            ip, mac = match.groups()
            mac = mac.upper().replace('-', ':')  # Padroniza formato MAC
            ip_mac[ip].append(mac)

    # IPs com mais de um MAC = conflito
    conflicts = {ip: macs for ip, macs in ip_mac.items() if len(macs) > 1}
    return conflicts

# ==================== RENOVA O IP VIA DHCP (DE ACORDO COM O SO) ====================
def renew_ip():
    """Força a renovação do endereço IP (libera e pega novo via DHCP)"""
    print(f"{VIOLET}[+] Renovando endereço IP...{RESET}")
    if OS == "Linux":
        run_command("dhclient -r && dhclient", capture_output=False)
    elif OS == "Windows":
        run_command("ipconfig /release && ipconfig /renew", capture_output=False)
    elif OS == "Darwin":
        run_command("sudo ifconfig en0 down && sudo ifconfig en0 up", capture_output=False)
        run_command("sudo ipconfig set en0 DHCP", capture_output=False)
    print(f"{MIDNIGHT}[+] IP renovado. Execute novamente para verificar.{RESET}")

# ==================== FUNÇÃO PRINCIPAL ====================
def main():
    # Exibe o SO detectado
    print(f"{CYAN}[*] ShadowSec Net Diag v1.0 | SO Detectado: {OS}{RESET}")

    # Gera timestamps para relatório e nome do arquivo
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamp_readable = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    # Pega informações locais
    my_ip, my_mac = get_local_info()
    network = get_local_network() or "Desconhecida"

    # Exibe informações iniciais
    print(f"{CYAN}[*] Diagnóstico iniciado em: {timestamp_readable}{RESET}")
    print(f"{CYAN}[*] Sua máquina: {my_ip} ({my_mac}){RESET}")
    print(f"{CYAN}[*] Rede detectada: {network}{RESET}\n")

    # Escaneia hosts
    hosts = scan_for_hosts(network)
    # Garante que o próprio dispositivo apareça na lista
    if my_ip != "Unknown" and not any(h[0] == my_ip for h in hosts):
        hosts.append((my_ip, my_mac))

    # Lista hosts encontrados
    print(f"{MIDNIGHT}[+] Hosts ativos encontrados: {len(hosts)}{RESET}")
    for ip, mac in hosts:
        status = "(Você)" if ip == my_ip else ""
        print(f"  - {ip} ({mac}) {status}")

    # Verifica conflitos
    conflicts = check_ip_conflicts(network)

    # Se houver conflitos, alerta e oferece solução
    if conflicts:
        print(f"\n{BLOOD_RED}[!] CONFLITOS DE IP DETECTADOS!{RESET}")
        for ip, macs in conflicts.items():
            print(f"  → IP {ip} usado por múltiplos MACs: {', '.join(macs)}")
        print("\n[VIOLET]Soluções recomendadas:{RESET}")
        print("   • Renovar IP automaticamente")
        print("   • Reservar IP por MAC no roteador")

        choice = input(f"\n{VIOLET}[?] Deseja renovar o IP agora? (s/n): {RESET}")
        if choice.lower() == 's':
            renew_ip()
    else:
        print(f"\n{MIDNIGHT}[+] Nenhum conflito detectado. Rede estável e segura!{RESET}")

    # Gera e salva relatório JSON com timestamp único
    report = {
        "timestamp": timestamp_readable,
        "os": OS,
        "your_device": {"ip": my_ip, "mac": my_mac},
        "network": network,
        "hosts": hosts,
        "conflicts": conflicts
    }
    filename = f"shadowsec_net_report_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print(f"{VIOLET}[+] Relatório salvo como: {filename}{RESET}")

# ==================== EXECUÇÃO DO SCRIPT ====================
if __name__ == "__main__":
    main()
