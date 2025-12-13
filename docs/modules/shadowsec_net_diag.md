🛜 ShadowSec Net Diag Edition🛡️
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)



Ferramenta: **ShadowSec Net Diag**  | Versão: 1.0 (Multi-Platform)
Objetivo: Módulo de Diagnóstico de Rede do ShadowSec Toolkit, para sistemas Debian-based e Windows e macOS, utilizando Python para portabilidade.
Autor: Luciano Valadão


### Descrição

Ferramenta avançada em Python para diagnóstico rápido de redes locais, com foco na **detecção e resolução de conflitos de IP**, o script identifica hosts ativos, verifica duplicidade de endereços IP e oferece soluções automáticas ou manuais.

Funciona de forma totalmente automática em **Linux, Windows e macOS**, detectando o sistema operacional e adaptando os comandos nativamente (ip, ipconfig, arp-scan, arp -a, nmap, dhclient, ipconfig /renew etc.).
Ideal para troubleshooting rápido em redes instáveis, auditorias de segurança, ambientes BYOD ou hotspots móveis.


### Principais Funcionalidades

- Detecção automática do SO e da sub-rede local
- Escaneamento de hosts ativos (com nmap -sn)
- Verificação de conflitos de IP via tabela ARP
- Exibição clara do seu dispositivo (IP + MAC)
- Renovação automática de IP via DHCP (segundo o SO)
- Geração de relatório detalhado em JSON com **timestamp único** no nome do arquivo
- Interface colorida no terminal (violeta, vermelho sangue, azul noite e ciano)
- Código totalmente comentado e modular, pronto para integração em toolkits maiores


### Detalhes técnicos

- **Detecção automática do sistema operacional** via `platform.system()` (Linux, Windows, Darwin/macOS)

- **Obtenção de informações locais**:
  - IPv4 e MAC address da máquina atual, usando comandos nativos:
    - Linux: `ip route` + `ip link`
    - Windows: `ipconfig` + `getmac`
    - macOS: `ipconfig getifaddr` + `ifconfig`

- **Detecção inteligente da sub-rede local** (/24 padrão) a partir do gateway ou source IP da rota padrão

- **Escaneamento de hosts ativos** com `nmap -sn` (ping scan):
  - Extrai IPs e, quando disponível, MAC addresses e fabricantes
  - Inclui automaticamente o dispositivo local na lista de hosts

- **Verificação de conflitos de IP**:
  - Linux: utiliza `arp-scan` para scan completo da rede
  - Windows/macOS: analisa a tabela ARP local via `arp -a`
  - Detecta IPs associados a múltiplos MAC addresses (indicativo claro de conflito)

- **Renovação automática de endereço IP** via DHCP, adaptada ao SO:
  - Linux: `dhclient -r && dhclient`
  - Windows: `ipconfig /release && ipconfig /renew`
  - macOS: desativa/ativa interface + `ipconfig set DHCP`

- **Interface interativa** com opção de renovar IP imediatamente ao detectar conflito

- **Geração de relatório completo** em formato JSON:
  - Inclui timestamp legível e técnico
  - Dados do dispositivo local, rede detectada, lista de hosts, conflitos encontrados e SO
  - Nome do arquivo com timestamp único: `shadowsec_net_report_YYYY-MM-DD_HH-MM-SS.json`

- **Saída colorida no terminal** utilizando códigos ANSI (violeta, vermelho sangue, azul noite, ciano gelado)

- **Código 100% comentado linha a linha**, facilitando manutenção, estudo e extensão
- **Zero dependências externas obrigatórias** (exceto `nmap` recomendado e `arp-scan` no Linux para máxima precisão)


### Exemplo de Uso

bash
```
sudo python3 shadowsec_net_diag.py
```


### Requisitos recomendados

nmap (para escaneamento completo de hosts)
 arp-scan (Linux – para detecção precisa de conflitos)


### Saída Esperada

Lista de dispositivos na rede
Alertas em vermelho caso haja conflitos
Opção interativa para renovar IP
Relatório salvo como: shadowsec_net_report_YYYY-MM-DD_HH-MM-SS.json


### Ideal para

Diagnóstico rápido em redes com instabilidade
Pentest e auditoria de redes locais
Ambientes BYOD ou hotspots móveis
Aprendizado de redes e scripting multi-plataforma


Licença: Distribuído sob licença MIT. 2025
Você pode usar, modificar e distribuir livremente mantendo os créditos.

Contato: Luciano Valadão - ```lukk.valadao@gmail.com```



