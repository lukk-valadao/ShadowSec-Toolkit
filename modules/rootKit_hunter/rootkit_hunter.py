#!/usr/bin/env python3
# ShadowSec Toolkit - Rootkit / Backdoor Scanner (Python Edition)
# Autor: Luciano Valadão
# Versão: 1.0
#
# Objetivo:
#   - Examinar sinais iniciais de rootkits/backdoors
#   - Automatizar passos usados em análise forense
#   - Coletar dados sobre processos, portas, serviços e binários suspeitos
#
# Obs:
#   Este script não altera nada no sistema — é somente diagnóstico.

import subprocess
import os

# Cores básicas para realce visual (opcional)
Y = "\033[33m"   # Amarelo
G = "\033[32m"   # Verde
R = "\033[31m"   # Vermelho
RESET = "\033[0m"

# -------------------------------------------------------------
# Função para imprimir o banner inicial
# -------------------------------------------------------------
def banner():
    print(f"{G}============================================")
    print(f"         ShadowSec Rootkit Hunter 1.0")
    print(f"============================================{RESET}")

# -------------------------------------------------------------
# Função auxiliar para executar comandos externos de forma segura
# -------------------------------------------------------------
def run_cmd(cmd):
    """
    Executa um comando no shell e retorna sua saída como string.
    - capture_output=True para não poluir o console com ruído desnecessário
    - text=True para receber saída como string ao invés de bytes
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Erro ao executar '{cmd}': {e}"

# -------------------------------------------------------------
# Função de seção (apenas para formatação bonitinha)
# -------------------------------------------------------------
def section(title):
    print(f"\n{Y}[*] {title}{RESET}")

# -------------------------------------------------------------
# 1 — Verifica processos que estão rodando como root
# -------------------------------------------------------------
def check_root_processes():
    """
    Processos executados pelo usuário root são críticos.
    Qualquer processo inesperado aqui pode indicar:
    - backdoor com privilégios elevados
    - serviço adulterado
    - rootkit com execução privilegiada
    """
    section("Processos rodando como root:")
    print(run_cmd("ps -U root -u root u"))

# -------------------------------------------------------------
# 2 — Verifica processos executando a partir de diretórios suspeitos
# -------------------------------------------------------------
def check_suspicious_dirs():
    """
    Rootkits e malwares ADORAM usar:
    - /tmp
    - /var/tmp
    - /dev
    - /run
    - diretórios ocultos (.nome)
    São locais permissivos, fáceis de escrever e com pouca vigilância.
    """
    dirs = r"/tmp|/var/tmp|/dev|/run|\.hidden|\.local"
    section("Processos executando a partir de diretórios suspeitos:")
    print(run_cmd(f"ps aux | grep -E '{dirs}' | grep -v grep"))

# -------------------------------------------------------------
# 3 — Verifica processos com executáveis apagados (deleted)
# -------------------------------------------------------------
def check_deleted_binaries():
    """
    Processo rodando com o executável DELETADO é um dos sinais
    MAIS CLAROS de malware em atividade.
    (backdoors costumam apagar o arquivo após carregar na memória)
    """
    section("Processos com executáveis deletados:")
    print(run_cmd("ls -l /proc/*/exe 2>/dev/null | grep deleted"))

# -------------------------------------------------------------
# 4 — Lista portas abertas e processos associados
# -------------------------------------------------------------
def check_open_ports():
    """
    Portas abertas inesperadas geralmente indicam:
    - backdoor TCP
    - botnet implantando listener
    - tunelamento reverso
    """
    section("Portas abertas e processos associados:")
    print(run_cmd("ss -tulpn"))

# -------------------------------------------------------------
# 5 — Serviços suspeitos do systemd
# -------------------------------------------------------------
def check_systemd_services():
    """
    Rootkits modernos adoram:
    - criar serviços falsos
    - modificar serviços legítimos
    Aqui procuramos por unidades com estado:
    - failed
    - dead
    - error
    E por nomes estranhos como 'python', 'tmp', 'test'.
    """
    section("Serviços systemd suspeitos:")
    print(run_cmd("systemctl list-units --type=service --all | grep -E 'failed|dead|error|tmp|test|python|sh'"))

# -------------------------------------------------------------
# 6 — Unidades criadas manualmente (persistência)
# -------------------------------------------------------------
def check_manual_units():
    """
    Muitos backdoors usam systemd para persistência.
    Aqui listamos:
    - serviços manuais em /etc/systemd/system
    - serviços do usuário em ~/.config/systemd/user
    """
    section("Unidades manuais instaladas em /etc/systemd/system:")
    print(run_cmd("ls -1 /etc/systemd/system/"))

    user_systemd = os.path.expanduser("~/.config/systemd/user/")
    if os.path.exists(user_systemd):
        section("Unidades no ~/.config/systemd/user:")
        print(run_cmd(f"ls -1 {user_systemd}"))

# -------------------------------------------------------------
# 7 — Verificação de integridade (debsums)
# -------------------------------------------------------------
def check_debsums():
    """
    debsums informa se algum binário do sistema foi alterado.
    Isso detecta:
    - substituição de comandos do sistema por trojans
    - adulteração de bibliotecas
    """
    section("Binários alterados (debsums):")
    if subprocess.call("command -v debsums >/dev/null 2>&1", shell=True) == 0:
        print(run_cmd("sudo debsums -s"))
    else:
        print(f"{R}debsums não instalado.{RESET}")

# -------------------------------------------------------------
# 8 — RKHunter e Chkrootkit (se instalados)
# -------------------------------------------------------------
def check_rkhunter_chkrootkit():
    """
    Executa scanners clássicos de rootkits.
    Não detectam tudo, mas ajudam muito na triagem inicial.
    """
    section("RKHunter:")
    if subprocess.call("command -v rkhunter >/dev/null 2>&1", shell=True) == 0:
        print(run_cmd("sudo rkhunter --check --sk"))
    else:
        print(f"{R}rkhunter não instalado.{RESET}")

    section("Chkrootkit:")
    if subprocess.call("command -v chkrootkit >/dev/null 2>&1", shell=True) == 0:
        print(run_cmd("sudo chkrootkit"))
    else:
        print(f"{R}chkrootkit não instalado.{RESET}")

# -------------------------------------------------------------
# Função principal — fluxo do script
# -------------------------------------------------------------
def main():
    banner()
    check_root_processes()
    check_suspicious_dirs()
    check_deleted_binaries()
    check_open_ports()
    check_systemd_services()
    check_manual_units()
    check_debsums()
    check_rkhunter_chkrootkit()

    print(f"\n{G}[✓] Varredura concluída.{RESET}")
    print("Analise os resultados acima para sinais de atividade suspeita.")

# Execução direta
if __name__ == "__main__":
    main()

