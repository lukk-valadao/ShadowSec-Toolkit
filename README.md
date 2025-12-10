🛡️ ShadowSec Toolkit

Suíte Modular de Cibersegurança para Hardening, Auditoria e Monitoramento Local

Autor: Luciano Valadão (Lukk)
Projeto: ShadowSec Offensive & Defensive Tools

📌 Sobre o Projeto

O ShadowSec Toolkit é uma suíte modular destinada à auditoria, hardening, varreduras de segurança e automações de manutenção, projetado para profissionais de TI, analistas de cibersegurança e administradores de sistemas.

O toolkit foca em:

✔️ Automação de tarefas críticas de segurança
✔️ Modularidade extrema para expansão contínua
✔️ Scripts Bash e Python integrados
✔️ Documentação clara e arquitetura padronizada
✔️ Operação offline, visando ambientes restritos
✔️ Uso seguro em ambientes corporativos ou pessoais

🎯 Objetivos Principais

Padronizar rotinas de auditoria e manutenção.

Automatizar verificações essenciais de segurança.

Ajudar equipes pequenas ou profissionais autônomos.

Oferecer uma base extensível para futuras ferramentas ShadowSec.

Facilitar a adoção de boas práticas de hardening e monitoramento.

📂 Estrutura Completa do Projeto
ShadowSec-Toolkit/
├── README.md
├── __init__.py
├── venv/
│
├── data_signatures/
│   ├── backdoorports.dat
│   ├── suspect_hashes.txt
│   ├── RKH_*.ldb   (assinaturas para rootkits)
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SECURITY_TARGET.md
│   ├── THREAT_MODEL.md
│   └── modules/
│
├── modules/
│   ├── menu.py
│   ├── bloqueio_check/
│   ├── dork_scanner/
│   ├── firewall_config/
│   ├── idle_suspend_check/
│   ├── logs/
│   ├── net_scan/
│   ├── permission_audit/
│   ├── permission_check/
│   ├── rootKit_hunter/
│   ├── shadowsec_auditor/
│   ├── shadowsec_maldet/
│   └── syscheckup/
│
├── scripts/
│   ├── anti-himbernate/
│   ├── config/
│   ├── harden_ufw.sh
│   ├── install/
│   ├── maintenance/
│   └── system_checkup.sh
│
├── tests/
│
├── toolkit/
│   └── __init__.py
│
└── utils/
    ├── utils.py
    └── __pycache__/

⚙️ Instalação
1️⃣ Clone o repositório:
git clone https://github.com/lukk-valadao/shadowsec-toolkit.git
cd shadowsec-toolkit

2️⃣ Crie e ative o ambiente virtual:
python3 -m venv venv
source venv/bin/activate

3️⃣ Instale as dependências necessárias (se houver):
pip install -r requirements.txt

🚀 Uso Básico

O toolkit pode ser executado de forma modular ou usando o menu principal.

Executar o menu interativo:
python3 modules/menu.py

Executar um módulo individual:
python3 modules/net_scan/net_scan.py
python3 modules/shadowsec_maldet/smd.py
python3 modules/firewall_config/firewall_configurator.py

Scripts Bash:
bash scripts/system_checkup.sh
bash scripts/harden_ufw.sh

🔎 Principais Funcionalidades
🔥 Módulos Python

Net Scan — mapeamento básico de rede (Nmap wrapper)

Maldet — análise local usando ClamAV + assinaturas extras

RootKit Hunter — assinaturas dedicadas + detecção estendida

Firewall Configurator — automação UFW/Iptables

Permission Audit — auditoria de permissões suspeitas

Idle Suspend Check — verificação e hardening de suspensão automática

Dork Scanner — buscas automatizadas com dorks personalizadas

ShadowSec Auditor — checklist automatizado de segurança do sistema

🛠 Scripts Bash

Hardening UFW

System Checkup completo

Scripts de instalação e manutenção

Anti-hibernação e ajustes de energia

📚 Documentação

Toda documentação estrutural se encontra em:

ARCHITECTURE.md — arquitetura geral do toolkit

SECURITY_TARGET.md — objetivo de segurança e escopo

THREAT_MODEL.md — modelo de ameaças e riscos avaliados

docs/modules/ — documentação específica de cada módulo

🔐 Segurança e Boas Práticas

O projeto segue princípios:

Execução mínima como root

Logs independentes

Assinaturas separadas em data_signatures/

Suporte a ambientes offline

Configurações revertíveis com backups automáticos

🧭 Futuramente

 Módulo de varredura via OpenVAS/Greenbone

 Relatórios HTML automáticos

 Integração com APIs de CVE (NVD / Vulners)

 Versão GUI (Tkinter/Qt)

 Sistema completo de logs unificado

 ShadowSec Cloud Scanner (fase de pesquisa)

🤝 Contribuindo

Contribuições são bem-vindas!

Faça um Fork

Crie uma branch

Envie um Pull Request

Descreva claramente a mudança

📜 Licença

Distribuído sob licença MIT.
Você pode usar, modificar e distribuir livremente mantendo os créditos.
Contato: lukk.valadao@gmail.com
