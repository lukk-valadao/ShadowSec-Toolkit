#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowSec Rootkit Hunter ULTIMATE v2.0
Autor original: Luciano Valadão (Lukk)
Versão turbinada pela sua vagabundona favorita

Modo rápido → 45 segundos
Modo completo → pega até rootkit que sua mãe nem sonha
"""
import os
import json
import subprocess
import hashlib
import sys
from datetime import datetime

# ========================= CORES =========================
R = "\033[31m"; G = "\033[32m"; Y = "\033[33m"; C = "\033[36m"; B = "\033[34m"; M = "\033[35m"; RESET = "\033[0m"

def banner():
    print(f"""{M}
    ╔══════════════════════════════════════════════════════╗
              SHADOWSEC ROOTKIT HUNTER — ULTIMATE v2.0
                     Feito pra pegar até o diabo
    ╚══════════════════════════════════════════════════════╝{RESET}""")

# ========================= AUX =========================
def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
    except:
        return ""

def section(title):
    print(f"\n{Y}[★] {title}{RESET}")

# ========================= CHECAGENS =========================
def check_root_processes():
    section("Processos root suspeitos (em /tmp, /dev/shm, etc)")
    out = run("ps aux | awk 'NR>1 && $1==\"root\" && $11 ~ /tmp|dev.shm|var.tmp|home/'")
    print(out if out else f"{G}Nenhum suspeito encontrado.{RESET}")
    return out

def check_deleted_binaries():
    section("Binários deletados em execução (sinal clássico de malware)")
    out = run("ls -l /proc/*/exe 2>/dev/null | grep deleted")
    print(out if out else f"{G}Nenhum binário deletado.{RESET}")
    return out

def check_suspicious_dirs():
    section("Processos rodando de diretórios temporários/ocultos")
    dirs = r"/tmp|/var/tmp|/dev/shm|\.cache|\.local|\.hidden"
    out = run(f"ps aux | grep -E '{dirs}' | grep -v grep")
    print(out if out else f"{G}Nenhum encontrado.{RESET}")
    return out

def check_open_ports():
    section("Portas abertas (ss)")
    print(run("ss -tulpn"))

def check_hidden_processes():
    section("Processos ocultos — cross-check ps × /proc × lsof")
    ps = set(run("ps -eo pid --no-headers").split())
    proc = set([d for d in os.listdir("/proc") if d.isdigit()])
    lsof = set(run("lsof -nP -i -F p 2>/dev/null | grep ^p | cut -c2-").split())

    hidden_proc = ps - proc
    hidden_lsof = ps - lsof

    if hidden_proc or hidden_lsof:
        print(f"{R}⚠ Processos invisíveis detectados!{RESET}")
        if hidden_proc: print(f"  → Invisíveis para /proc: {hidden_proc}")
        if hidden_lsof: print(f"  → Invisíveis para lsof: {hidden_lsof}")
    else:
        print(f"{G}Nenhum processo oculto.{RESET}")
    return {"hidden_proc": list(hidden_proc), "hidden_lsof": list(hidden_lsof)}

def check_kernel_modules():
    section("Módulos do kernel suspeitos")
    raw = run("lsmod")
    sus = []
    for line in raw.splitlines()[1:]:
        name = line.split()[0]
        if len(name) < 4 or name.startswith("_") or any(k in name.lower() for k in ["hide","rootkit","rk_","lkm","reptile","diamorphine"]):
            sus.append(line)
            print(f"{R}→ POSSÍVEL ROOTKIT: {line}{RESET}")
    if not sus:
        print(f"{G}Nenhum módulo suspeito.{RESET}")
    return {"raw": raw, "suspicious": sus}

def check_systemd_persistence():
    section("Unidades systemd manuais (persistência comum)")
    print(f"{C}/etc/systemd/system/{RESET}")
    print(run("ls -la /etc/systemd/system/ 2>/dev/null | tail -n +3") or "vazio")
    user_dir = os.path.expanduser("~/.config/systemd/user")
    if os.path.isdir(user_dir):
        print(f"{C}{user_dir}{RESET}")
        print(run(f"ls -la {user_dir}"))

def check_debsums():
    section("Integridade de pacotes (debsums)")
    if os.system("command -v debsums >/dev/null") == 0:
        print(run("sudo debsums -cs 2>/dev/null") or f"{G}Nenhum pacote alterado.{RESET}")
    else:
        print(f"{Y}debsums não instalado → sudo apt install debsums{RESET}")

def run_external_scanners():
    section("Executando rkhunter e chkrootkit (se instalados)")
    if os.system("command -v rkhunter >/dev/null") == 0:
        print(f"{C}→ rkhunter{RESET}")
        os.system("sudo rkhunter --check --sk --no-mail")
    if os.system("command -v chkrootkit >/dev/null") == 0:
        print(f"{C}→ chkrootkit{RESET}")
        os.system("sudo chkrootkit")

# ========================= RELATÓRIO =========================
def save_reports(data):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"shadowsec_ultimate_{ts}"

    # TXT bonito
    with open(f"{base}.txt", "w") as f:
        f.write(f"SHADOWSEC ROOTKIT HUNTER ULTIMATE — {ts}\n")
        f.write("="*60 + "\n\n")
        for k, v in data.items():
            f.write(f"[{k.upper()}]\n")
            if isinstance(v, dict):
                f.write(json.dumps(v, indent=2, ensure_ascii=False))
            else:
                f.write(str(v))
            f.write("\n\n")

    # JSON puro
    with open(f"{base}.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # HTML rápido e lindo
    with open(f"{base}.html", "w") as f:
        f.write(f"""<html><head><title>ShadowSec Report {ts}</title>
        <style>body{{font-family: monospace; background:#000; color:#0f0; padding:20px;}}
        h1{{color:#f0f}} pre{{background:#111; padding:15px; border-left:5px solid #f0f}}</style></head>
        <body><h1>ShadowSec Ultimate Report — {ts}</h1>""")
        for k, v in data.items():
            f.write(f"<h2>{k.replace('_',' ').title()}</h2><pre>{json.dumps(v, indent=2)}</pre>")
        f.write("</body></html>")

    print(f"\n{G}[✓] Relatórios salvos:{RESET}")
    print(f"   → {base}.txt")
    print(f"   → {base}.json")
    print(f"   → {base}.html")

# ========================= MENU =========================
def menu():
    while True:
        os.system("clear")
        banner()
        print(f"""{C}
    [1] Scan RÁPIDO      (45 seg – ideal pra triagem)
    [2] Scan COMPLETO    (tudo + rkhunter/chkrootkit)
    [3] Só processos ocultos + portas escondidas
    [4] Sair
        {RESET}""")
        op = input(f"\n{Y}Escolha o modo de scan → {RESET}")

        results = {}
        results["timestamp"] = datetime.now().isoformat()

        if op == "1":
            check_root_processes()
            check_deleted_binaries()
            check_suspicious_dirs()
            check_open_ports()
            check_kernel_modules()
            save_reports(results)

        elif op == "2":
            check_root_processes()
            check_deleted_binaries()
            check_suspicious_dirs()
            check_open_ports()
            check_hidden_processes()
            check_kernel_modules()
            check_systemd_persistence()
            check_debsums()
            run_external_scanners()
            results.update({
                "hidden_processes": check_hidden_processes(),
                "kernel_modules": check_kernel_modules(),
            })
            save_reports(results)

        elif op == "3":
            check_hidden_processes()
            check_open_ports()

        elif op == "4":
            print(f"{M}Finalizado, logs gerados{RESET}")
            sys.exit(0)

        input(f"\n{Y}Pressione ENTER pra voltar ao menu…{RESET}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{R}Execute como root, caralho! (sudo python3 shadowsec_ultimate.py){RESET}")
        sys.exit(1)
    menu()
