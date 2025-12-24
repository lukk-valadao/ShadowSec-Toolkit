#!/usr/bin/env python3
# .py
# ShadowSec Toolkit - Módulo de verificação de suspensão automática por inatividade
# Por: Luciano Valadão

# modules/auditor.py
import subprocess, datetime, json, os
from utils.utils import log, run_cmd
#from utils import log, run_cmd

def audit_system(output_dir="reports"):
    log("[Audit] Iniciando auditoria de segurança...")

    # Cria diretório de relatório
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = os.path.join(output_dir, f"audit_{timestamp}.json")

    results = {}

    # ClamAV
    log("[Audit] Verificando malware...")
    out, err, rc = run_cmd("clamscan -r /home --bell -i")
    results["clamav"] = {"output": out, "return_code": rc}

    # RKHunter
    log("[Audit] Executando RKHunter...")
    out, err, rc = run_cmd("rkhunter --check --sk --nocolors")
    results["rkhunter"] = {"output": out, "return_code": rc}

    # Lynis
    log("[Audit] Executando Lynis...")
    out, err, rc = run_cmd("lynis audit system --quiet")
    results["lynis"] = {"output": out, "return_code": rc}

    # Nmap
    log("[Audit] Escaneando portas locais...")
    out, err, rc = run_cmd("nmap -sS localhost")
    results["nmap"] = {"output": out, "return_code": rc}

    # Salva relatório JSON
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log(f"[Audit] Relatório salvo em: {report_path}")
    return report_path

