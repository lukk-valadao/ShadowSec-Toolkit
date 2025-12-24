#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ShadowSec Rootkit Scan v1.0

Autor: Luciano Valadão

Objetivo:
Ferramenta de detecção de rootkits e persistências maliciosas em sistemas Linux.
Realiza múltiplas verificações de integridade, processos ocultos, módulos do kernel,
persistência via systemd, hooks LD_PRELOAD, portas abertas e integração com scanners externos.

Gera dois tipos de relatório:
- RAW (bruto, sem formatação)
- READABLE (quebrado e legível para análise humana)
"""
import os
import subprocess
import textwrap
import sys
from datetime import datetime  # ← Correto: importa a classe diretamente

# ========================= CORES ANSI =========================
# Escape codes para saída colorida no terminal (UX e legibilidade)

R = "\033[31m"   # Vermelho → alertas / perigo
G = "\033[32m"   # Verde → sucesso / OK
Y = "\033[33m"   # Amarelo → aviso / seção
C = "\033[36m"   # Ciano → informações
B = "\033[34m"   # Azul
M = "\033[35m"   # Magenta → identidade visual
RESET = "\033[0m"  # Reseta cores

def banner():
    print(f"""{M}
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ║
    ║ ▓▓                █ █ █ NEON DISTRICT ROOTKIT SCANNER █ █ █             ▓▓ ║
    ║ ▓▓                                                                      ▓▓ ║
    ║ ▓▓          ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗   ██╗          ▓▓ ║
    ║ ▓▓          ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║   ██║          ▓▓ ║
    ║ ▓▓          ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║         ▓▓ ║
    ║ ▓▓          ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║         ▓▓ ║
    ║ ▓▓          ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝         ▓▓ ║
    ║ ▓▓          ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝          ▓▓ ║
    ║ ▓▓                                                                      ▓▓ ║
    ║ ▓▓                       SHADOWSEC ROOTKIT SCAN v1.0                    ▓▓ ║
    ║ ▓▓    システム侵入検知モードが有効になりました / BREACH MODE ACTIVE     ▓▓ ║
    ║ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    {RESET}""")

# ========================= AUX =========================
def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except:
        return ""

def section(title):
    print(f"\n{Y}[★] {title}{RESET}")

def alert(msg):
    print(f"{R}[!] {msg}{RESET}")

def success(msg):
    print(f"{G}[✓] {msg}{RESET}")

def save_readable_report(report_content, output_dir=".", prefix="shadowsec_rtk"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # ← Correto agora
    base_filename = f"{prefix}_{timestamp}"
    raw_path = os.path.join(output_dir, f"{base_filename}_RAW.log")
    readable_path = os.path.join(output_dir, f"{base_filename}_READABLE.txt")

    # RAW
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # READABLE (quebra linhas longas)
    wrapped = ""
    for line in report_content.splitlines():
        if len(line) > 120:
            wrapped += "\n".join(textwrap.wrap(line, width=120)) + "\n"
        else:
            wrapped += line + "\n"

    with open(readable_path, "w", encoding="utf-8") as f:
        f.write(wrapped)

    return readable_path, raw_path

# ========================= CHECAGENS (retornam string para relatório) =========================
def check_root_processes():
    section("Processos root suspeitos (em /tmp, /dev/shm, etc)")
    out = run("ps aux | awk 'NR>1 && $1==\"root\" && $11 ~ /tmp|dev/shm|var.tmp|home/|cache/'")
    if out:
        print(out)
        return out
    else:
        success("Nenhum suspeito encontrado.")
        return "Nenhum suspeito encontrado."

def check_deleted_binaries():
    section("Binários deletados em execução (clássico de rootkit)")
    out = run("ls -l /proc/*/exe 2>/dev/null | grep ' (deleted)'")
    if out:
        alert("BINÁRIOS DELETADOS ENCONTRADOS:")
        print(out)
        return out
    else:
        success("Nenhum binário deletado em execução.")
        return "Nenhum binário deletado em execução."

def check_suspicious_dirs():
    section("Processos rodando de diretórios temporários/ocultos")
    dirs = r"/tmp|/var/tmp|/dev/shm|\.cache|\.local|\.hidden|\.\."
    out = run(f"ps aux | grep -E '{dirs}' | grep -v grep")
    if out:
        print(out)
        return out
    else:
        success("Nenhum processo em diretório suspeito.")
        return "Nenhum processo em diretório suspeito."

def check_open_ports():
    section("Portas abertas no sistema (ss + lsof)")
    ss_out = run("ss -tulpn 2>/dev/null || netstat -tulpn 2>/dev/null")
    lsof_out = run("lsof -i -nP 2>/dev/null || echo 'lsof não disponível'")
    full_out = f"ss:\n{ss_out}\n\nlsof:\n{lsof_out}"
    print(full_out)
    return full_out

def check_hidden_processes():
    section("Processos ocultos — ps × /proc × lsof")
    ps_pids = set(run("ps -eo pid --no-headers").split())
    proc_pids = set(d for d in os.listdir("/proc") if d.isdigit())
    lsof_out = run("lsof -nP -i -F p 2>/dev/null | grep '^p' | cut -c2-")
    lsof_pids = set(lsof_out.split()) if lsof_out else set()

    hidden_from_proc = ps_pids - proc_pids
    hidden_from_lsof = ps_pids - lsof_pids

    result = ""
    if hidden_from_proc or hidden_from_lsof:
        alert("PROCESSOS OCULTOS DETECTADOS!")
        if hidden_from_proc:
            result += f"Invisíveis para /proc: {hidden_from_proc}\n"
            print(f"{R}→ Invisíveis para /proc: {hidden_from_proc}{RESET}")
        if hidden_from_lsof:
            result += f"Invisíveis para lsof: {hidden_from_lsof}\n"
            print(f"{R}→ Invisíveis para lsof: {hidden_from_lsof}{RESET}")
    else:
        success("Nenhum processo oculto detectado.")
        result = "Nenhum processo oculto detectado."
    return result

def check_kernel_modules():
    section("Módulos do kernel suspeitos")
    raw = run("lsmod")
    sus = []
    # Keywords mais precisas (evita falsos positivos em módulos legítimos curtos)
    keywords = ["rootkit", "rk_", "reptile", "diamorphine", "knull", "adorng", "xhide", "suterusu", "hideproc"]
    for line in raw.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 1: continue
        name = parts[0].lower()
        if any(k in name for k in keywords):
            sus.append(line.strip())
            alert(f"POSSÍVEL ROOTKIT LKM → {parts[0]}")
    if not sus:
        success("Nenhum módulo suspeito encontrado.")
    return raw + "\n\n" + ("Módulos suspeitos encontrados:\n" + "\n".join(sus) if sus else "Nenhum módulo suspeito.")

def check_systemd_persistence():
    section("Persistência via systemd")
    paths = ["/etc/systemd/system/", "~/.config/systemd/user/"]
    output = ""
    for p in paths:
        path = os.path.expanduser(p)
        if os.path.isdir(path):
            output += f"{path}:\n"
            out = run(f"ls -la '{path}' 2>/dev/null | tail -n +3")
            output += out + "\n\n"
            print(f"{C}{path}{RESET}")
            print(out if out else "vazio")
        else:
            output += f"{path} → não existe\n"
            print(f"{Y}{path} → não existe{RESET}")
    return output.strip()

def check_debsums():
    section("Integridade de pacotes (debsums)")
    if os.system("command -v debsums >/dev/null") == 0:
        print(f"{C}Executando debsums -cs...{RESET}")
        out = run("debsums -cs 2>/dev/null")
        if out:
            alert("PACOTES ALTERADOS ENCONTRADOS:")
            print(out)
            return out
        else:
            success("Todos os pacotes estão íntegros!")
            return "Todos os pacotes estão íntegros."
    else:
        msg = "debsums não instalado → sudo apt install debsums"
        print(f"{Y}{msg}{RESET}")
        return msg

def check_ld_preload():
    section("LD_PRELOAD Hooks")
    out = run("grep -R \"LD_PRELOAD\" /etc/ 2>/dev/null")
    if out:
        alert("LD_PRELOAD definido encontrado!")
        print(out)
        return out
    else:
        success("LD_PRELOAD limpo.")
        return "LD_PRELOAD limpo."

def check_essential_binaries():
    section("Hashes MD5 de binários críticos")
    bins = [
        "/bin/ls", "/bin/cat", "/bin/bash", "/usr/bin/sudo",
        "/usr/bin/login", "/usr/bin/passwd", "/usr/bin/ssh",
        "/usr/bin/ps", "/usr/bin/top", "/usr/bin/ss", "/usr/bin/lsof", "/bin/netstat"
    ]
    result = ""
    for b in bins:
        if os.path.exists(b):
            hash_out = run(f"md5sum {b}")
            result += f"{hash_out}\n"
        else:
            result += f"[!] Binário ausente: {b}\n"
    print(result.strip())
    return result.strip()

def check_rkhunter_chkrootkit():
    section("Status de scanners externos")
    rkh = "instalado" if os.system("command -v rkhunter >/dev/null") == 0 else "não instalado"
    chk = "instalado" if os.system("command -v chkrootkit >/dev/null") == 0 else "não instalado"
    msg = f"rkhunter: {rkh}\nchkrootkit: {chk}"
    if rkh == "não instalado":
        msg += "\n→ sudo apt install rkhunter"
    if chk == "não instalado":
        msg += "\n→ sudo apt install chkrootkit"
    print(msg)
    return msg

def run_external_scanners():
    section("Executando scanners externos (se disponíveis)")
    executed = []
    if os.system("command -v rkhunter >/dev/null") == 0:
        print(f"{C}→ rkhunter em execução...{RESET}")
        os.system("rkhunter --check --sk --cronjob 2>/dev/null")
        executed.append("rkhunter executado")
    if os.system("command -v chkrootkit >/dev/null") == 0:
        print(f"{C}→ chkrootkit em execução...{RESET}")
        os.system("chkrootkit")
        executed.append("chkrootkit executado")
    return "\n".join(executed) if executed else "Nenhum scanner externo disponível."

# ========================= MENU =========================
def menu():
    while True:
        os.system("clear")
        banner()
        print(f"""{C}
    [1] Scan RÁPIDO (triagem rápida)
    [2] Scan COMPLETO (máxima detecção)
    [3] Caça fantasma (processos ocultos + portas)
    [4] Sair
        {RESET}""")
        op = input(f"\n{Y}Escolha o modo → {RESET}").strip()

        report_content = "========= SHADOWSEC ROOTKIT SCAN v1.0 =========\n\n"

        if op == "1":
            print(f"{C}[+] MODO RÁPIDO ATIVADO{RESET}")
            report_content += check_root_processes() + "\n\n"
            report_content += check_deleted_binaries() + "\n\n"
            report_content += check_suspicious_dirs() + "\n\n"
            report_content += check_open_ports() + "\n\n"
            report_content += check_kernel_modules() + "\n\n"

        elif op == "2":
            print(f"{C}[+] MODO COMPLETO ATIVADO{RESET}")
            report_content += check_root_processes() + "\n\n"
            report_content += check_deleted_binaries() + "\n\n"
            report_content += check_suspicious_dirs() + "\n\n"
            report_content += check_open_ports() + "\n\n"
            report_content += check_hidden_processes() + "\n\n"
            report_content += check_kernel_modules() + "\n\n"
            report_content += check_systemd_persistence() + "\n\n"
            report_content += check_debsums() + "\n\n"
            report_content += check_ld_preload() + "\n\n"
            report_content += check_essential_binaries() + "\n\n"
            report_content += check_rkhunter_chkrootkit() + "\n\n"
            report_content += run_external_scanners() + "\n\n"

        elif op == "3":
            print(f"{C}[+] CAÇANDO FANTASMAS...{RESET}")
            report_content += check_hidden_processes() + "\n\n"
            report_content += check_open_ports() + "\n\n"

        elif op in ["4", "sair", "exit", "q"]:
            print(f"{M}Saindo do ShadowSec Rootkit Scan...{RESET}")
            sys.exit(0)

        else:
            print(f"{R}Opção inválida.{RESET}")
            input("Pressione ENTER para continuar...")
            continue

        readable, raw = save_readable_report(report_content)
        print(f"\n{G}[✓] SCAN FINALIZADO! Relatórios salvos:{RESET}")
        print(f" → {readable} (legível)")
        print(f" → {raw} (bruto)")
        input(f"\n{Y}Pressione ENTER para voltar ao menu…{RESET}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{R}[!] Execute como root: sudo python3 rtk.py{RESET}")
        sys.exit(1)
    menu()
