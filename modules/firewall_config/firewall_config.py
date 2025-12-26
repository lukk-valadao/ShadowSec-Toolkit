#!/usr/bin/env python3
# ================================================================
# ShadowSec Toolkit - Firewall Configurator
# Autor: Luciano Valadão
# Descrição:
#   Hardening do UFW com backup, reset, configuração interativa e
#   relatório completo (hash, portas, alterações críticas e auditoria).
# ================================================================

import subprocess
import os
import hashlib
from datetime import datetime
import json
import sys

REPORT_DIR = os.path.expanduser("~/ShadowSec/reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# -------------------------------
# Função para executar comandos
# -------------------------------
def run_cmd(cmd, capture_output=False):
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, text=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None
        )
        return result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"[!] Erro ao executar: {cmd}")
        if capture_output:
            print(e.stderr)
        sys.exit(1)

# -------------------------------
# Validação de privilégios root/sudo
# -------------------------------
def require_sudo():
    if os.geteuid() != 0:
        print("[!] Este script requer privilégios administrativos (sudo).")
        try:
            subprocess.run("sudo -v", shell=True, check=True)
        except subprocess.CalledProcessError:
            print("[!] Falha ao validar sudo. Abortando.")
            sys.exit(1)
    print("[+] Permissão sudo confirmada.")

# -------------------------------
# Backup das regras atuais
# -------------------------------
def backup_rules():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(REPORT_DIR, f"ufw_backup_{timestamp}.txt")
    print(f"[+] Fazendo backup das regras atuais em {backup_file}...")
    run_cmd(f"sudo ufw status numbered > {backup_file}")
    return backup_file

# -------------------------------
# Hash do backup para integridade
# -------------------------------
def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# -------------------------------
# Reset do UFW e configuração padrão
# -------------------------------
def reset_ufw():
    print("[+] Resetando regras do UFW...")
    run_cmd("sudo ufw --force reset")
    print("[+] Aplicando política padrão: deny incoming / allow outgoing...")
    run_cmd("sudo ufw default deny incoming")
    run_cmd("sudo ufw default allow outgoing")

# -------------------------------
# Configuração interativa
# -------------------------------
def configure_rules():
    config = {}
    # SSH
    allow_ssh = input("Deseja permitir acesso SSH (porta 22)? [s/N]: ").strip().lower()
    if allow_ssh == 's':
        run_cmd("sudo ufw allow 22/tcp")
        print("[+] Porta SSH (22) liberada.")
        config['SSH'] = "Liberado"
    else:
        print("[-] SSH bloqueado por padrão.")
        config['SSH'] = "Bloqueado"

    # HTTP/HTTPS
    allow_web = input("Deseja permitir HTTP e HTTPS? [s/N]: ").strip().lower()
    if allow_web == 's':
        run_cmd("sudo ufw allow 80/tcp")
        run_cmd("sudo ufw allow 443/tcp")
        print("[+] HTTP/HTTPS liberados.")
        config['HTTP'] = "Liberado"
        config['HTTPS'] = "Liberado"
    else:
        print("[-] Portas web bloqueadas.")
        config['HTTP'] = "Bloqueado"
        config['HTTPS'] = "Bloqueado"

    return config

# -------------------------------
# Estado final do firewall
# -------------------------------
def firewall_status():
    status = run_cmd("sudo ufw status verbose", capture_output=True)
    return status

# -------------------------------
# Resumo de portas abertas
# -------------------------------
def open_ports_summary():
    ports = run_cmd("sudo ufw status | grep 'ALLOW' | awk '{print $1,$2}'", capture_output=True)
    return ports.strip().split('\n') if ports else []

# -------------------------------
# Último usuário que modificou as regras
# -------------------------------
def last_user_modification(file_path):
    try:
        output = run_cmd(f"sudo ausearch -f {file_path} -m MODIFY -ts today", capture_output=True)
        for line in reversed(output.splitlines()):
            if "uid=" in line:
                uid_part = line.split("uid=")[1].split()[0]
                user = run_cmd(f"getent passwd {uid_part} | cut -d: -f1", capture_output=True).strip()
                return user
    except:
        # fallback: dono do arquivo
        return run_cmd(f"stat -c %U {file_path}", capture_output=True).strip()
    return "Desconhecido"

# -------------------------------
# Geração de relatório
# -------------------------------
def generate_report(backup_file, config, status, open_ports):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    hash_backup = hash_file(backup_file)
    last_user = last_user_modification("/etc/ufw/user.rules")
    report_json = os.path.join(REPORT_DIR, f"firewall_report_{timestamp}.json")
    report_md = os.path.join(REPORT_DIR, f"firewall_report_{timestamp}.md")

    report_data = {
        "usuario": os.getenv("USER"),
        "backup_file": backup_file,
        "backup_hash": hash_backup,
        "alteracoes_aplicadas": config,
        "estado_atual": status,
        "portas_abertas": open_ports,
        "ultimo_usuario_modificacao": last_user,
        "timestamp": timestamp
    }

    # JSON
    with open(report_json, "w") as f:
        json.dump(report_data, f, indent=4)

    # Markdown
    with open(report_md, "w") as f:
        f.write(f"# 🛡 ShadowSec Firewall Report — {timestamp}\n")
        f.write(f"**Usuário:** {report_data['usuario']}\n\n")
        f.write(f"**Backup das regras:** `{backup_file}`\n")
        f.write(f"**Hash do backup:** `{hash_backup}`\n\n")
        f.write("## Alterações aplicadas:\n")
        for k, v in config.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Estado atual do firewall:\n```\n")
        f.write(status + "\n```\n")
        f.write("\n## Resumo de portas abertas:\n```\n")
        for port in open_ports:
            f.write(f"{port}\n")
        f.write("```\n")
        f.write(f"\n**Último usuário que modificou regras:** {last_user}\n")
        f.write(f"\n[✔] Relatório gerado com sucesso.\n")

    print(f"[+] Relatórios gerados:\n - {report_json}\n - {report_md}")

# -------------------------------
# Ativar logging e habilitar firewall
# -------------------------------
def enable_firewall():
    print("[+] Ativando logs do UFW...")
    run_cmd("sudo ufw logging on")
    print("[+] Ativando UFW...")
    run_cmd("sudo ufw --force enable")

# -------------------------------
# Execução principal
# -------------------------------
def main():
    print("🛡️  ShadowSec Firewall Configurator v1.0 🛡️")
    require_sudo()
    backup_file = backup_rules()
    reset_ufw()
    config = configure_rules()
    enable_firewall()
    status = firewall_status()
    open_ports = open_ports_summary()
    generate_report(backup_file, config, status, open_ports)
    print("\n[✔] Configuração concluída com sucesso.")

if __name__ == "__main__":
    main()
