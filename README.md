![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

# ShadowSec Toolkit

🔐 Uma suíte modular de cibersegurança para auditoria, limpeza e proteção de sistemas.

---

## 🎯 Objetivos do Projeto

- Automatizar tarefas comuns de manutenção e segurança.
- Modularidade para fácil expansão e manutenção.
- Código aberto, bem estruturado e documentado.
- Facilitar o trabalho de profissionais de TI e entusiastas de segurança.

---

## 📁 Estrutura do Projeto

```
shadowsec-toolkit/
├── docs/
│ ├── Security Target (Common Criteria)(docs/SECURITY_TARGET.md)
│ ├── Modelo de Ameaças(docs/THREAT_MODEL.md)
│ ├── Arquitetura do Toolkit(docs/ARCHITECTURE.md)
│ ├── modules (Documentação dos Módulos)
│   ├── bloqueio_check.md
│   ├── net_scan.md
│   ├── system_checkup.md
│   └── user-installed-cleaner.md
├── modules/
│ ├── bloqueio_check.py
│ ├── idle_suspend_check.py
│ ├── net_scan.py
│ └── suspect_hashes.txt
├── scripts/
│ ├── install/
│ │ ├── install.sh
│ │ └── install_clamav.sh
│ ├── config/
│ │ └── configurar_suspensao.sh
│ ├── maintenance/
│ │ ├── user-installed-cleaner.sh
│ │ └── update-git.sh
│ └── system_checkup.sh
├── tests/ # Ideal manter para futuros testes automatizados
│ └── (vazio no momento)
├── toolkit/
│ └── init.py # Pacote para funções comuns do toolkit
├── utils/ # Funções helpers e utilitários
│ └── init.py
├── venv/ # Ambiente virtual (normalmente ignorado pelo git)
├── .gitignore
├── README.md
```
---

## ⚙️ Como Usar

1. Clone o repositório:

```bash
git clone https://github.com/lukk-valadao/shadowsec-toolkit.git
cd shadowsec-toolkit

2. Ative o ambiente virtual (se aplicável):

python3 -m venv venv
source venv/bin/activate

3. Execute scripts ou módulos conforme necessidade.

🛠 Sobre as Pastas
docs/: Documentação detalhada dos módulos e scripts.

modules/: Scripts principais em Python e arquivos de dados relacionados.

scripts/: Scripts shell organizados por função:

install/: Scripts de instalação.

config/: Scripts de configuração.

maintenance/: Scripts de manutenção e atualização.

Arquivos utilitários diretamente em scripts/.

tests/: Espaço reservado para testes automatizados futuros.

toolkit/: Código base para funcionalidades comuns entre módulos.

utils/: Funções auxiliares e helpers para o projeto.

venv/: Ambiente virtual Python para dependências isoladas.
