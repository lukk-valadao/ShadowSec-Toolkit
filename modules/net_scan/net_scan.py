#!/usr/bin/env python3
# net_scan.py
# ShadowSec Toolkit - Módulo scan de rede.
# Por: Luciano Valadão

import sys
import nmap

def scan_network(network):
    nm = nmap.PortScanner()
    print(f"Iniciando scan na rede: {network}")
    nm.scan(hosts=network, arguments='-sn')  # Scan do tipo ping scan

    hosts_up = []
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            print(f"Host ativo encontrado: {host}")
            hosts_up.append(host)
    if not hosts_up:
        print("Nenhum host ativo encontrado na rede.")
    return hosts_up

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python net_scan.py <rede>")
        print("Exemplo: python net_scan.py 192.168.0.0/24")
        sys.exit(1)

    network = sys.argv[1]
    scan_network(network)

