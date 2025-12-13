#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rootkit Hunter PRO v1.1 — ShadowSec Edition
autor: Luciano Valadão

Descrição:
    Scanner avançado de rootkits e anomalias de segurança.
    Inclui:
        - Verificação de processos root suspeitos
        - Procfs cross-check (ps vs /proc vs lsof)
        - Portas abertas escondidas
        - Módulos de kernel suspeitos
        - Hashes de binários críticos
        - Verificação de LD_PRELOAD e syscalls
        - Detecção de processos em diretórios anômalos
        - Aviso se RKHunter e Chkrootkit não estão instalados
        - Relatório final TXT + JSON
"""

import os
import json
import subprocess
from datetime import datetime

# ------------------------------
# Funções auxiliares
# ------------------------------

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output

# ------------------------------
# 1. Verificar processos root suspeitos
# ------------------------------

def check_root_processes():
    output = run("ps aux | grep '^root'")
    suspicious = []
    for line in output.splitlines():
        if any(path in line for path in ["/tmp", "/dev/shm", "/var/tmp", "/home"]):
            suspicious.append(line)
    return {"raw": output, "suspicious": suspicious}

# ------------------------------
# 2. Cross-check ps /proc / lsof
# ------------------------------

def cross_check_processes():
    ps_list = run("ps -eo pid").split()
    proc_list = [pid for pid in os.listdir("/proc") if pid.isdigit()]
    lsof_list = set()

    lsof_raw = run("lsof -nP | awk '{print $2}'")
    for pid in lsof_raw.split():
        if pid.isdigit():
            lsof_list.add(pid)

    hidden_in_proc = set(ps_list) - set(proc_list)
    hidden_in_lsof = set(ps_list) - lsof_list

    return {
        "hidden_in_proc": list(hidden_in_proc),
        "hidden_in_lsof": list(hidden_in_lsof)
    }

# ------------------------------
# 3. Portas abertas por processos invisíveis
# ------------------------------

def check_hidden_ports():
    ss_raw = run("ss -tulnp")
    lsof_raw = run("lsof -nP -i")

    hidden = []
    for line in ss_raw.splitlines():
        if "pid=" in line and "lsof" not in line:
            pid = line.split("pid=")[-1].split(",")[0]
            if pid not in lsof_raw:
                hidden.append(line)

    return {"ss": ss_raw, "hidden": hidden}

# ------------------------------
# 4. Módulos de kernel suspeitos
# ------------------------------

def check_kernel_modules():
    lsmod_raw = run("lsmod")
    suspicious = []
    for line in lsmod_raw.splitlines()[1:]:
        cols = line.split()
        if len(cols) >= 3:
            name = cols[0]
            if len(name) < 3 or name.startswith("_"):
                suspicious.append(line)
    return {"raw": lsmod_raw, "suspicious": suspicious}

# ------------------------------
# 5. Hashes de binários críticos
# ------------------------------

BINARIES = ["/bin/ls", "/bin/ps", "/usr/bin/top", "/usr/bin/ss", "/usr/bin/find"]


def check_binary_hashes():
    results = {}
    for b in BINARIES:
        if os.path.exists(b):
            md5 = run(f"md5sum {b}").split()[0]
            results[b] = md5
    return results

# ------------------------------
# 6. LD_PRELOAD, syscall hooking
# ------------------------------

def check_ld_preload():
    preload = os.environ.get("LD_PRELOAD", "<empty>")
    kall = run("cat /proc/kallsyms | grep -E 'hook|intercept|override' || true")
    return {"LD_PRELOAD": preload, "Suspicious_kallsyms": kall}

# ------------------------------
# 7. Check RKHunter & Chkrootkit
# ------------------------------

def check_tools():
    tools = {}

    rkh = run("which rkhunter || echo 'not_installed'")
    chk = run("which chkrootkit || echo 'not_installed'")

    tools["rkhunter"] = "installed" if "rkhunter" in rkh and "not_installed" not in rkh else "not_installed"
    tools["chkrootkit"] = "installed" if "chkrootkit" in chk and "not_installed" not in chk else "not_installed"

    return tools

# ------------------------------
# 8. Relatório final
# ------------------------------

def generate_report(data):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    txt_path = f"rootkit_report_{timestamp}.txt"
    json_path = f"rootkit_report_{timestamp}.json"

    # TXT
    with open(txt_path, "w") as f:
        f.write("==== ROOTKIT HUNTER PRO v4.0 — ShadowSec Edition ===\n\n")
        for k, v in data.items():
            f.write(f"## {k}\n")
            f.write(json.dumps(v, indent=4))
            f.write("\n\n")

    # JSON
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    return txt_path, json_path

# ------------------------------
# MAIN
# ------------------------------

def main():
    results = {}

    results["root_processes"] = check_root_processes()
    results["cross_check"] = cross_check_processes()
    results["hidden_ports"] = check_hidden_ports()
    results["kernel_modules"] = check_kernel_modules()
    results["binary_hashes"] = check_binary_hashes()
    results["preload_syscalls"] = check_ld_preload()
    results["external_tools"] = check_tools()

    txt, js = generate_report(results)

    print("\n[+] Relatórios gerados:")
    print(f" - TXT:  {txt}")
    print(f" - JSON: {js}")


if __name__ == "__main__":
    main()
