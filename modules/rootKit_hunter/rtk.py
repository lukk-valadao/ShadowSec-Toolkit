#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowSec Rootkit Hunter ULTIMATE v2.1
Autor: Luciano Valadão (Lukk)
Versão turbinada
→ Relatórios agora 100% completos em TODOS os modos
→ Mais rápido, mais perigoso
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
    ╔══════════════════════════════════════════════════════════════╗
    ║ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ║
    ║ ▓▓     █ █ █   NEON DISTRICT ROOTKIT SCANNER   █ █ █      ▓▓ ║
    ║ ▓▓                                                        ▓▓ ║
    ║ ▓▓   ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗  ▓▓ ║
    ║ ▓▓   ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║  ▓▓ ║
    ║ ▓▓   ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║  ▓▓ ║
    ║ ▓▓   ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║  ▓▓ ║
    ║ ▓▓   ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝  ▓▓ ║
    ║ ▓▓   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝   ▓▓ ║
    ║ ▓▓                                                        ▓▓ ║
    ║ ▓▓         SHADOWSEC ROOTKIT HUNTER v9.9.9                ▓▓ ║
    ║ ▓▓システム侵入検知モードが有効になりました / BREACH MODE ACTIVE  ▓▓ ║
    ║ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ║
    ╚══════════════════════════════════════════════════════════════╝
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

# ========================= CHECAGENS =========================
def check_root_processes():
    section("Processos root suspeitos (em /tmp, /dev/shm, etc)")
    out = run("ps aux | awk 'NR>1 && $1==\"root\" && $11 ~ /tmp|dev/shm|var.tmp|home/|cache/'")
    if out:
        print(out)
    else:
        success("Nenhum suspeito encontrado.")
    return out

def check_deleted_binaries():
    section("Binários deletados em execução (clássico de rootkit)")
    out = run("ls -l /proc/*/exe 2>/dev/null | grep ' (deleted)'")
    if out:
        alert("BINÁRIOS DELETADOS ENCONTRADOS:")
        print(out)
    else:
        success("Nenhum binário deletado em execução.")
    return out

def check_suspicious_dirs():
    section("Processos rodando de diretórios temporários/ocultos")
    dirs = r"/tmp|/var/tmp|/dev/shm|\.cache|\.local|\.hidden|\.\."
    out = run(f"ps aux | grep -E '{dirs}' | grep -v grep")
    if out:
        print(out)
    else:
        success("Nenhum processo em diretório suspeito.")
    return out

def check_open_ports():
    section("Portas abertas no sistema (ss)")
    out = run("ss -tulpn 2>/dev/null || netstat -tulpn 2>/dev/null")
    print(out if out else "Nenhuma porta detectada (raro).")
    return out

def check_hidden_processes():
    section("Processos ocultos — ps × /proc × lsof")
    ps_pids   = set(run("ps -eo pid --no-headers").split())
    proc_pids = set(d for d in os.listdir("/proc") if d.isdigit())
    lsof_pids = set(run("lsof -nP -i -F p 2>/dev/null | grep '^p' | cut -c2-").split())

    hidden_from_proc = ps_pids - proc_pids
    hidden_from_lsof = ps_pids - lsof_pids

    if hidden_from_proc or hidden_from_lsof:
        alert("PROCESSOS OCULTOS DETECTADOS!")
        if hidden_from_proc:
            print(f"{R}→ Invisíveis para /proc: {hidden_from_proc}{RESET}")
        if hidden_from_lsof:
            print(f"{R}→ Invisíveis para lsof: {hidden_from_lsof}{RESET}")
    else:
        success("Nenhum processo oculto detectado.")

    return {
        "hidden_from_proc": list(hidden_from_proc),
        "hidden_from_lsof": list(hidden_from_lsof),
        "total_hidden": len(hidden_from_proc) + len(hidden_from_lsof)
    }

def check_kernel_modules():
    section("Módulos do kernel suspeitos")
    raw = run("lsmod")
    sus = []
    keywords = ["hide", "rootkit", "rk_", "lkm", "reptile", "diamorphine", "knull", "adorng", "xhide"]

    for line in raw.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 1: continue
        name = parts[0]
        if (len(name) < 4 or name.startswith("_") or
            any(k in name.lower() for k in keywords)):
            sus.append(line.strip())
            alert(f"POSSÍVEL ROOTKIT LKM → {name}")

    if not sus:
        success("Nenhum módulo suspeito encontrado.")
    return {"suspicious_modules": sus, "total_sus": len(sus), "raw_lsmod": raw}

def check_systemd_persistence():
    section("Persistência via systemd (comum em malware moderno)")
    paths = ["/etc/systemd/system/", "~/.config/systemd/user/"]
    output = ""

    for p in paths:
        path = os.path.expanduser(p)
        if os.path.isdir(path):
            print(f"{C}{path}{RESET}")
            out = run(f"ls -la '{path}' 2>/dev/null | tail -n +3")
            print(out if out else "vazio")
            output += f"{path}:\n{out}\n\n"
        else:
            print(f"{Y}{path} → não existe{RESET}")
    return output.strip()

def check_debsums():
    section("Integridade de pacotes Debian/Ubuntu (debsums)")
    if os.system("command -v debsums >/dev/null") == 0:
        print(f"{C}Executando debsums -cs (pode demorar um pouco)...{RESET}")
        out = run("debsums -cs 2>/dev/null")
        if out:
            alert("PACOTES ALTERADOS ENCONTRADOS:")
            print(out)
        else:
            success("Todos os pacotes estão íntegros!")
        return out
    else:
        print(f"{Y}debsums não instalado → sudo apt install debsums{RESET}")
        return "debsums não instalado"

def run_external_scanners():
    section("Executando scanners externos (se disponíveis)")
    rkh = os.system("command -v rkhunter >/dev/null") == 0
    chk = os.system("command -v chkrootkit >/dev/null") == 0

    if rkh:
        print(f"{C}→ rkhunter em execução (pode demorar)...{RESET}")
        os.system("rkhunter --check --sk --no-mail --cronjob")
    if chk:
        print(f"{C}→ chkrootkit em execução...{RESET}")
        os.system("chkrootkit")
    return {"rkhunter": rkh, "chkrootkit": chk}

# ========================= RELATÓRIO FINAL =========================
def save_reports(data):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"shadowsec_ultimate_{ts}"

    # Contar alertas
    alerts = 0
    if data.get("deleted_binaries"): alerts += 1
    if data.get("kernel_modules", {}).get("total_sus", 0) > 0: alerts += 1
    if data.get("hidden_processes", {}).get("total_hidden", 0) > 0: alerts += 1

    data["scan_summary"] = {
        "timestamp": datetime.now().isoformat(),
        "hostname": run("hostname"),
        "alerts_found": alerts,
        "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    }

    # TXT
    with open(f"{base}.txt", "w") as f:
        f.write(f"SHADOWSEC ROOTKIT HUNTER ULTIMATE v2.1 — {ts}\n")
        f.write(f"Host: {data['scan_summary']['hostname']}\n")
        f.write(f"Alertas críticos: {alerts}\n")
        f.write("="*70 + "\n\n")
        for k, v in data.items():
            if k == "scan_summary": continue
            f.write(f"[{k.upper().replace('_', ' ')}]\n")
            f.write(str(v).strip() + "\n\n")

    # JSON
    with open(f"{base}.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # HTML lindo
    with open(f"{base}.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>ShadowSec Report {ts}</title>
<style>
  body {{font-family: 'Courier New', monospace; background:#000; color:#0f0; padding:30px;}}
  h1 {{color:#ff00ff; text-align:center;}}
  h2 {{color:#00ffff; border-bottom: 2px solid #ff00ff; padding:10px;}}
  pre {{background:#111; padding:20px; border-left:8px solid #f0f; overflow-x:auto;}}
  .alert {{color:#ff0000; font-weight:bold;}}
  .ok {{color:#00ff00;}}
</style></head>
<body>
<h1>ShadowSec Rootkit Hunter ULTIMATE — {ts}</h1>
<p><b>Host:</b> {data['scan_summary']['hostname']} | <b>Alertas:</b> <span class="alert">{alerts}</span></p>
""")
        for k, v in data.items():
            if k == "scan_summary": continue
            title = k.replace("_", " ").title()
            f.write(f"<h2>{title}</h2><pre>{json.dumps(v, indent=2, ensure_ascii=False)}</pre>")
        f.write("</body></html>")

    print(f"\n{G}[✓] SCAN FINALIZADO! Relatórios salvos:{RESET}")
    print(f"   → {base}.txt")
    print(f"   → {base}.json")
    print(f"   → {base}.html  ← abre no navegador, fica uma PORNÔGRAFIA de lindo")
    if alerts > 0:
        alert(f"{alerts} ALERTA(S) CRÍTICO(S) ENCONTRADO(S) — checa logo essa porra!")

# ========================= MENU =========================
def menu():
    while True:
        os.system("clear")
        banner()
        print(f"""{C}
    [1] Scan RÁPIDO (45 seg – triagem insana)
    [2] Scan COMPLETO (tudo + rkhunter + chkrootkit)
    [3] Só processos ocultos + portas (caça fantasma)
    [4] Sair
        {RESET}""")

        op = input(f"\n{Y}Escolha o modo, meu macho → {RESET}")

        results = {"timestamp": datetime.now().isoformat()}

        if op == "1":
            print(f"{C}[+] MODO RÁPIDO ATIVADO — vai voando...{RESET}")
            results.update({
                "modo": "Scan Rápido",
                "root_processes": check_root_processes(),
                "deleted_binaries": check_deleted_binaries(),
                "suspicious_dirs": check_suspicious_dirs(),
                "open_ports": check_open_ports(),
                "kernel_modules": check_kernel_modules(),
            })

        elif op == "2":
            print(f"{C}[+] MODO COMPLETO — agora fodeu, vai pegar até o capeta{RESET}")
            results.update({
                "modo": "Scan Completo",
                "root_processes": check_root_processes(),
                "deleted_binaries": check_deleted_binaries(),
                "suspicious_dirs": check_suspicious_dirs(),
                "open_ports": check_open_ports(),
                "hidden_processes": check_hidden_processes(),
                "kernel_modules": check_kernel_modules(),
                "systemd_persistence": check_systemd_persistence(),
                "debsums": check_debsums(),
                "external_scanners": run_external_scanners(),
            })

        elif op == "3":
            print(f"{C}[+] Caçando fantasmas...{RESET}")
            results.update({
                "modo": "Apenas processos ocultos + portas",
                "hidden_processes": check_hidden_processes(),
                "open_ports": check_open_ports(),
            })

        elif op == "4" or op.lower() in ["sair", "exit", "q"]:
            print(f"{M}Até a próxima, gostoso… quando quiser eu abro de novo ♡{RESET}")
            sys.exit(0)
        else:
            print(f"{R}Opção inválida, otário.{RESET}")
            input("Enter pra continuar...")
            continue

        save_reports(results)
        input(f"\n{Y}Pressione ENTER pra voltar ao menu…{RESET}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{R}[!] Executa como root, porra! → sudo python3 shadowsec_ultimate.py{RESET}")
        sys.exit(1)
    menu()
