# 🛡️ ShadowSec Toolkit


![OS Compatibility](https://img.shields.io/badge/OS-Linux%20|%20Windows-blueviolet.svg)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)

![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

![License](https://img.shields.io/badge/license-MIT-green.svg)



Suíte Modular de Cibersegurança para Hardening, Auditoria e Monitoramento Local

**Autor:** Luciano Valadão (Lukk)

**Projeto:** ShadowSec Offensive & Defensive Tools



---



## 📌 Sobre o Projeto



O ShadowSec Toolkit é uma suíte modular destinada à auditoria, hardening, varreduras de segurança e automações de manutenção, projetado para profissionais de TI, analistas de cibersegurança e administradores de sistemas.



**Principais focos:**

- Automação de tarefas críticas de segurança

- Modularidade extrema para expansão contínua

- Scripts Bash e Python integrados

- Documentação clara e arquitetura padronizada

- Operação offline, visando ambientes restritos

- Uso seguro em ambientes corporativos ou pessoais



---



## 🎯 Objetivos Principais



- Padronizar rotinas de auditoria e manutenção

- Automatizar verificações essenciais de segurança

- Ajudar equipes pequenas ou profissionais autônomos

- Oferecer uma base extensível para futuras ferramentas ShadowSec

- Facilitar a adoção de boas práticas de hardening e monitoramento



---



## 📂 Estrutura do Projeto


```
ShadowSec-Toolkit/
├── README.md
├── __init__.py
├── venv/
│
├── data_signatures/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SECURITY_TARGET.md
│   ├── THREAT_MODEL.md
│   └── modules/nome_do_modulo.md
│
├── modules/
│   ├── __init__.py
│   ├── menu.py
│   │
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
│   ├── shadowsec_net_diag/
│   ├── shadowsec_maldet/
│   ├── syscheckup/
│   └── venv/
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
    ├── __init__.py
    ├── utils.py
    └── __pycache__/

```

---

## ⚙️ Instalação



1️ Clone o repositório:

bash
```
git clone https://github.com/lukk-valadao/shadowsec-toolkit.git

cd shadowsec-toolkit
```

2️ Crie e ative o ambiente virtual:

bash

Copiar código
```
python3 -m venv venv

source venv/bin/activate
```

3️ Instale dependências (se houver):

bash

Copiar código
```
pip install -r requirements.txt
```

🚀 Uso Básico

Executar o menu interativo:

bash

Copiar código
```
 //python3 modules/menu.py  **Em desenvolvimento, rodar scripts individualmente.**
```

Executar um módulo individual:

bash

Copiar código
```
python3 modules/syscheckup/sc.py

python3 modules/net_scan/net_scan.py

python3 modules/shadowsec_maldet/smd.py

python3 modules/firewall_config/firewall_configurator.py
```

Scripts Bash:


bash

Copiar código
```
bash scripts/system_checkup.sh

bash scripts/harden_ufw.sh
```

🔎 Principais Funcionalidades

Módulos Python
```
Net Scan: mapeamento básico de rede (Nmap wrapper)



Maldet: análise local usando ClamAV + assinaturas extras



RootKit Hunter: assinaturas dedicadas + detecção estendida



Firewall Configurator: automação UFW/Iptables



Permission Audit: auditoria de permissões suspeitas



Idle Suspend Check: verificação e hardening de suspensão automática



Dork Scanner: buscas automatizadas com dorks personalizadas



ShadowSec Auditor: checklist automatizado de segurança do sistema



ShadowSec Net Diag: diagnóstico de Rede, conflito de ip, para sistemas Debian-based e Windows e macOS
```


Scripts Bash
```
Hardening UFW



System Checkup completo



Scripts de instalação e manutenção



Anti-hibernação e ajustes de energia
```


📚 Documentação
```
ARCHITECTURE.md — arquitetura geral do toolkit



SECURITY_TARGET.md — objetivo de segurança e escopo



THREAT_MODEL.md — modelo de ameaças e riscos



docs/modules/ — documentação específica de cada módulo
```


🔐 Segurança e Boas Práticas

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

Faça um Fork



Crie uma branch



Envie um Pull Request



Descreva claramente a mudança



📜 Licença


Distribuído sob licença MIT.


Você pode usar, modificar e distribuir livremente mantendo os créditos.


Contato: Luciano Valadão - ```lukk.valadao@gmail.com```

---

