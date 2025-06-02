Documentação do Módulo net_scan.py
🔍 Função do módulo
O módulo net_scan.py é um scanner de rede que realiza varreduras básicas em IPs ou faixas de IPs usando o Nmap via a biblioteca python-nmap. Ele identifica portas abertas, serviços e seus estados. Esse módulo é parte fundamental do toolkit ShadowSec, ajudando o usuário a obter rapidamente uma visão geral dos dispositivos ativos na rede e seus serviços expostos.

🛠️ Requisitos
nmap instalado no sistema (sudo apt install nmap)

Ambiente virtual Python com python-nmap instalado:

python3 -m venv venv
source venv/bin/activate
pip install python-nmap
💻 Uso via Terminal

python net_scan.py 192.168.0.0/24
Você pode passar um IP único ou uma sub-rede CIDR para escanear.

🧠 Explicação do código
Importações

import nmap
import argparse
import sys
Usa argparse para ler argumentos da linha de comando, sys para encerrar em caso de erro e nmap para interagir com o binário Nmap.

Função scan_target()

Executa o Nmap com o argumento -sV (descoberta de serviços).

Itera sobre os hosts encontrados, listando:

Hostname

Estado (up/down)

Protocolos detectados (geralmente tcp)

Portas abertas, estado e nome do serviço

Bloco principal

if __name__ == \"__main__\":
    parser = argparse.ArgumentParser(...)
Permite que o script seja usado de forma autônoma pela linha de comando.

🧪 Exemplos de saída
plaintext

[+] Iniciando varredura em: 192.168.0.0/24

Host: 192.168.0.1 (router.local)
Estado: up

Protocolo: tcp
Porta: 22     Estado: open       Serviço: ssh
Porta: 80     Estado: open       Serviço: http
✅ Status
 Finalizado

 Testado localmente

 Compatível com Linux


