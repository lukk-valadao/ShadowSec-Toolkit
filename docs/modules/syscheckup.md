# 🛡️ SysCheckUp v1.0 - Python Edition

![OS Compatibility](https://img.shields.io/badge/OS-Linux%20|%20Windows-blueviolet.svg)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)

![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

![License](https://img.shields.io/badge/license-MIT-green.svg)


**Ferramenta:** SysCheck-Up | **Versão:** 1.0 (Python Port)
**Objetivo:** Painel interativo de verificação, limpeza e segurança para sistemas **Debian-based** e **Windows**, utilizando Python para portabilidade.
**Autor:** Luciano Valadão

---

## 💡 Sobre o Projeto

O **SysCheckUp v1.0 (Python Edition)** é a transição das funcionalidades do script original em Bash para uma implementação em **Python**. O objetivo é manter a interface interativa e o conjunto de ferramentas de manutenção e segurança, mas garantir uma execução mais consistente e portátil entre os sistemas operacionais **Linux** e **Windows**.

A ferramenta utiliza a biblioteca `subprocess` do Python para orquestrar comandos de *shell* nativos (`apt`, `ufw`, `clamscan` no Linux, ou `choco`, `netsh`, `sfc` no Windows), adaptando a lógica para cada ambiente.

---

## 🔎 Funcionalidades Principais

| Categoria | Função | Linux (Comandos) | Windows (Comandos/Ferramentas) |
| :--- | :--- | :--- | :--- |
| **Manutenção** | **Atualizações** | `apt update/upgrade` (com tratamento de repositórios falhos). | `choco upgrade all` (via Chocolatey). |
| **Limpeza** | **Cache & Lixo** | `autoremove`, `autoclean`, `journalctl --vacuum`, Lixeira. | Limpeza de diretórios `Temp` e Lixeira (via PowerShell). |
| **Segurança** | **Firewall** | `ufw` status, instalação e configuração básica (fecha portas comuns). | `netsh advfirewall` status. |
| **Segurança** | **Scan de Vírus** | `clamscan` (com exclusão de Metasploit, se instalado). | Atualização das definições do Windows Defender. |
| **Auditoria** | **Integridade** | `debsums -s` (checa checksums de pacotes). | `sfc /scannow` (System File Checker). |
| **Auditoria** | **Pacotes Órfãos** | `deborphan` (identifica e remove). | Não aplicável (Apenas nota). |
| **Relatório** | **Info do Sistema** | `df -h`, `ss -tulnp`, `systemctl list-units`. | `wmic`, `netstat -ano`, `sc query state= all`. |
| **Utilidade** | **Backup** | Opções de backup Leve ou Completo usando `rsync`. | Backup de diretórios do usuário usando `shutil`. |

> **📌 Logs:** Todas as operações geram logs detalhados na pasta `Logs/` com *timestamp* automático, garantindo rastreabilidade.

---

## ⚙️ Requisitos e Execução

### Requisitos

* **Python:** Versão 3.8 ou superior.

### Execução (Modo Interativo)

Para iniciar o painel interativo, siga os passos abaixo no terminal:

#### 1. Clonar o Repositório

```bash
git clone [https://github.com/lukk-valadao/SysCheckUp.git](https://github.com/lukk-valadao/SysCheckUp.git)
cd SysCheckUp/modules
```
(Assumindo que o script se chama sc.py e está na pasta modules)
2. Executar o Script
Execute o script Python diretamente, utilizando o interpretador python3:
Bash
```
python3 sc.py
```

O script iniciará o menu, onde você pode selecionar os módulos a serem executados.
Estrutura dos Módulos
O projeto usa a função run_cmd e a biblioteca platform para decidir qual comando nativo deve ser executado, o que permite o suporte multiplataforma:
Python
if is_linux():
    run_cmd("sudo apt update")
elif is_windows():
    run_cmd("choco upgrade all -y")


📜 Licença

Distribuído sob licença MIT.

Você pode usar, modificar e distribuir livremente mantendo os créditos.

Contato: Luciano Valadão - ```lukk.valadao@gmail.com```
