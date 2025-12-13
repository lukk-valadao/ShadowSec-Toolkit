#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ShadowSec Toolkit – Rootkit Hunter PRO
# Autor: Luciano Valadão
# Versão: 1.0
#
# Objetivo:
# Scanner profissional de rootkits, módulos ocultos,
# serviços suspeitos, LD_PRELOAD, backdoors, e anomalias de kernel.
#

import subprocess
import datetime
import os
import textwrap
import re

# ----------------------------
# Funções auxiliares
# ----------------------------

def run(cmd):
    """Executa um comando e retorna a saída limpa."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return f"[ERRO] {cmd}\n{e.output}"

def save_readable_report(report_content, output_dir=".", prefix="rootkit_report"):
    """
    Gera dois relatórios:
    - RAW (completo)
    - READABLE (com quebras automáticas, 120 colunas)
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{prefix}_{timestamp}"

    raw_path = os.path.join(output_dir, f"{base_filename}_RAW.log")
    readable_path = os.path.join(output_dir, f"{base_filename}_READABLE.txt")

    # RAW
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # READABLE com wrapping
    wrapped = ""
    for line in report_content.splitlines():
        if len(line) > 120:
            wrapped += "\n".join(textwrap.wrap(line, width=120)) + "\n"
        else:
            wrapped += line + "\n"

    with open(readable_path, "w", encoding="utf-8") as f:
        f.write(wrapped)

    return readable_path, raw_path


# ----------------------------
# Módulos de Auditoria
# ----------------------------

def audit_root_processes():
    out = run("ps aux | grep '^root'")
    return f"[*] Root Processes:\n{out}\n"


def audit_kernel_modules():
    lsmod = run("lsmod")
    return f"[*] Kernel Modules:\n{lsmod}\n"


def audit_ports():
    ss_out = run("ss -tulnp")
    lsof_out = run("lsof -i -nP")
    return f"[*] Portas abertas (ss):\n{ss_out}\n[*] LSOF:\n{lsof_out}\n"


def check_hidden_files():
    hidden = run("find /proc -maxdepth 1 -type d -name '[0-9]*' -exec test ! -e '{}/exe' ';' -print")
    return f"[*] Processos ocultos em /proc:\n{hidden}\n"


def check_ld_preload():
    preload = run("grep -R \"LD_PRELOAD\" /etc/ 2>/dev/null")
    return f"[*] LD_PRELOAD Hooks:\n{preload}\n"


def compare_process_sources():
    ps_out = run("ps aux")
    proc_entries = run("ls -1 /proc | grep '^[0-9]'")
    lsof_out = run("lsof -nP")

    return (
        "[*] Comparação ps / proc / lsof\n\n"
        f"--- ps ---\n{ps_out}\n"
        f"--- /proc ---\n{proc_entries}\n"
        f"--- lsof ---\n{lsof_out}\n"
    )


def check_essential_binaries():
    bins = [
        "/bin/ls", "/bin/ps", "/usr/bin/top",
        "/usr/bin/ss", "/usr/bin/lsof", "/bin/netstat"
    ]

    result = "[*] Hashes de binários críticos:\n"
    for b in bins:
        if os.path.exists(b):
            hash_out = run(f"md5sum {b}")
            result += f"{hash_out}"
        else:
            result += f"[!] Binário ausente: {b}\n"

    return result + "\n"


def check_rkhunter_chkrootkit():
    rkh = "instalado" if os.path.exists("/usr/bin/rkhunter") else "não instalado"
    chk = "instalado" if os.path.exists("/usr/sbin/chkrootkit") else "não instalado"

    msg = "[*] RKHunter Status:\n"
    msg += f"rkhunter: {rkh}\n"

    msg += "\n[*] Chkrootkit Status:\n"
    msg += f"chkrootkit: {chk}\n"

    if rkh == "não instalado":
        msg += "\n→ Sugestão: sudo apt install rkhunter\n"
    if chk == "não instalado":
        msg += "\n→ Sugestão: sudo apt install chkrootkit\n"

    return msg + "\n"


# ----------------------------
# Gerador de relatório final
# ----------------------------

def generate_full_report():
    sections = []

    sections.append("========= ROOTKIT HUNTER PRO v1.0 — ShadowSec Edition =========\n")
    sections.append(audit_root_processes())
    sections.append(audit_ports())
    sections.append(audit_kernel_modules())
    sections.append(check_hidden_files())
    sections.append(check_ld_preload())
    sections.append(compare_process_sources())
    sections.append(check_essential_binaries())
    sections.append(check_rkhunter_chkrootkit())

    return "\n".join(sections)


# ----------------------------
# Execução principal
# ----------------------------

if __name__ == "__main__":
    print("[+] Executando auditoria SHADOWSEC ROOTKIT HUNTER v1.0...")
    report = generate_full_report()

    readable, raw = save_readable_report(report)
    print(f"[+] Relatório legível salvo em: {readable}")
    print(f"[+] Relatório RAW salvo em: {raw}")
    print("[+] Finalizado.")
