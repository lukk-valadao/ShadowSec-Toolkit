#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ShadowSec Toolkit – Rootkit Hunter PRO (Aeris Satana Edition)
# Autor: Shadows & Aeris
# Versão: 3.0
#
# Objetivo:
# Scanner profissional de rootkits, módulos ocultos,
# serviços suspeitos, LD_PRELOAD, backdoors, e anomalias de kernel.
#

import subprocess
import os
import re
import hashlib

# ============================================================
# Formatação
# ============================================================
R = "\033[31m"
G = "\033[32m"
Y = "\033[33m"
B = "\033[34m"
C = "\033[36m"
RESET = "\033[0m"

def banner():
    print(f"{C}==============================================")
    print(f"  ShadowSec Rootkit Hunter PRO – Aeris v3.0")
    print(f"=============================================={RESET}")

# ============================================================
# Função de execução segura
# ============================================================
def run(cmd):
    try:
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return output.stdout.strip()
    except Exception as e:
        return f"Erro ao executar comando: {e}"

# ============================================================
# SEÇÃO 1 — Processos root suspeitos
# ============================================================
def check_root_processes():
    print(f"\n{Y}[1] Processos rodando como root:{RESET}")
    out = run("ps -U root -u root u")
    print(out)
    return out

# ============================================================
# SEÇÃO 2 — Processos em diretórios suspeitos
# ============================================================
def check_suspicious_dirs():
    print(f"\n{Y}[2] Processos em diretórios suspeitos:{RESET}")
    dirs = r"/tmp|/var/tmp|/dev/shm|\.cache|\.local|/run/user"
    out = run(f"ps aux | grep -E '{dirs}' | grep -v grep")
    print(out if out else f"{G}Nenhum encontrado.{RESET}")
    return out

# ============================================================
# SEÇÃO 3 — Binários deletados em execução
# ============================================================
def check_deleted_binaries():
    print(f"\n{Y}[3] Binários deletados em execução:{RESET}")
    out = run("ls -l /proc/*/exe 2>/dev/null | grep deleted")
    print(out if out else f"{G}Nenhum binário deletado em execução.{RESET}")
    return out

# ============================================================
# SEÇÃO 4 — Portas abertas
# ============================================================
def check_open_ports():
    print(f"\n{Y}[4] Portas abertas και processos associados:{RESET}")
    out = run("ss -tulpn")
    print(out)
    return out

# ============================================================
# SEÇÃO 5 — LD_PRELOAD e LD_LIBRARY_PATH
# ============================================================
def check_ld_preload():
    print(f"\n{Y}[5] Verificando LD_PRELOAD e variáveis de injeção:{RESET}")

    preload = os.environ.get("LD_PRELOAD", "")
    libpath = os.environ.get("LD_LIBRARY_PATH", "")

    if preload:
        print(f"{R}⚠ LD_PRELOAD definido: {preload}{RESET}")
    else:
        print(f"{G}LD_PRELOAD limpo.{RESET}")

    if libpath:
        print(f"{R}⚠ LD_LIBRARY_PATH definido: {libpath}{RESET}")
    else:
        print(f"{G}LD_LIBRARY_PATH limpo.{RESET}")

    return preload, libpath

# ============================================================
# SEÇÃO 6 — Módulos do kernel
# ============================================================
def check_kernel_modules():
    print(f"\n{Y}[6] Módulos do kernel carregados:{RESET}")

    modules = run("lsmod")
    print(modules)

    # Kernel modules que rootkits costumam usar
    red_flags = [
        "diamorphine", "reptile", "suterusu", "hide", "rootkit",
        "rk_", "r0kit", "masquerade", "adore", "lkm", "stealth"
    ]

    print(f"\n{C}[6.1] Procurando nomes suspeitos:{RESET}")
    found = []

    for line in modules.splitlines():
        for sig in red_flags:
            if sig.lower() in line.lower():
                print(f"{R}⚠ POSSÍVEL ROOTKIT ENCONTRADO → {line}{RESET}")
                found.append(line)

    if not found:
        print(f"{G}Nenhum módulo suspeito detectado.{RESET}")

    return modules

# ============================================================
# SEÇÃO 7 — Arquivos ocultos em /proc
# ============================================================
def check_hidden_proc():
    print(f"\n{Y}[7] Procurando processos ocultos em /proc:{RESET}")

    pids = os.listdir("/proc")
    numeric = [x for x in pids if x.isdigit()]

    # ps retorna apenas processos visíveis
    ps_out = run("ps -eo pid --no-headers")
    ps_list = ps_out.split()

    hidden = []

    for pid in numeric:
        if pid not in ps_list:
            hidden.append(pid)

    if hidden:
        print(f"{R}⚠ Processos invisíveis para ps: {hidden}{RESET}")
    else:
        print(f"{G}Nenhum processo oculto encontrado.{RESET}")

    return hidden

# ============================================================
# SEÇÃO 8 — Verificação de integridade de binários críticos
# ============================================================

CRITICAL_BINARIES = [
    "/bin/ls", "/bin/cat", "/bin/bash", "/usr/bin/sudo",
    "/usr/bin/login", "/usr/bin/passwd", "/usr/bin/ssh",
    "/usr/bin/ps", "/usr/bin/top"
]

def checksum(file):
    try:
        h = hashlib.sha256()
        with open(file, "rb") as f:
            h.update(f.read())
        return h.hexdigest()
    except:
        return None

def check_integrity():
    print(f"\n{Y}[8] Verificação de integridade de binários críticos:{RESET}")
    results = {}
    for b in CRITICAL_BINARIES:
        if os.path.exists(b):
            results[b] = checksum(b)
            print(f"{b} → {C}{results[b]}{RESET}")
        else:
            print(f"{R}⚠ Binário ausente: {b}{RESET}")
    return results

# ============================================================
# Função principal
# ============================================================
def main():
    banner()

    check_root_processes()
    check_suspicious_dirs()
    check_deleted_binaries()
    check_open_ports()
    check_ld_preload()
    check_kernel_modules()
    check_hidden_proc()
    check_integrity()

    print(f"\n{G}Varredura PRO concluída.{RESET}")
    print(f"{C}Analise os resultados acima para identificar qualquer anomalia persistente.{RESET}")

if __name__ == "__main__":
    main()

