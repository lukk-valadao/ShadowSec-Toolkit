#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowSec Permission Auditor & Hardener
- Verifica permissões, dono e grupo conforme regras seguras.
- Permite aplicar correções interativamente ou em modo --auto.
- Registro em /var/log/shadowsec_permission_audit.log (se permitido) e ./shadowsec_permission_audit.log
"""

import os
import stat
import argparse
import datetime
import json
import sys
import shutil
from typing import Tuple, Dict

LOG_PATHS = ["/var/log/shadowsec_permission_audit.log", "./shadowsec_permission_audit.log"]

# ---------------------------
# Baseline de permissões seguras
# (Adapte conforme sua política)
# mode: octal, owner: username, group: groupname
# ---------------------------
SECURE_RULES = {
    "/etc/passwd":   {"mode": 0o644, "owner": "root", "group": "root"},
    "/etc/shadow":   {"mode": 0o640, "owner": "root", "group": "shadow"},
    "/etc/gshadow":  {"mode": 0o640, "owner": "root", "group": "shadow"},
    "/etc/sudoers":  {"mode": 0o440, "owner": "root", "group": "root"},
    "/root":         {"mode": 0o700, "owner": "root", "group": "root"},
    "/tmp":          {"mode": 0o1777, "owner": "root", "group": "root"},
    "/var/log":      {"mode": 0o750, "owner": "root", "group": "adm"},
    "/var/www":      {"mode": 0o755, "owner": "root", "group": "www-data"},  # diretório
    "/var/www/html": {"mode": 0o755, "owner": "www-data", "group": "www-data"},
    "/etc/ssh/sshd_config": {"mode": 0o600, "owner": "root", "group": "root"},
    "/usr/local/bin": {"mode": 0o755, "owner": "root", "group": "root"},
}

# ---------------------------
# Utilities: logging
# ---------------------------
def write_log_line(line: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full = f"[{ts}] {line}\n"
    written = False
    for p in LOG_PATHS:
        try:
            with open(p, "a") as f:
                f.write(full)
            written = True
        except Exception:
            continue
    # If none writable, write to stdout
    if not written:
        sys.stdout.write(full)

def log(msg: str):
    print(msg)
    write_log_line(msg)

# ---------------------------
# Resolve owner/group robustamente
# ---------------------------
def parse_passwd() -> Dict[int, str]:
    d = {}
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                if ":" not in line:
                    continue
                cols = line.strip().split(":")
                if len(cols) >= 3:
                    name = cols[0]
                    try:
                        uid = int(cols[2])
                        d[uid] = name
                    except ValueError:
                        continue
    except Exception:
        pass
    return d

def parse_group() -> Dict[int, str]:
    d = {}
    try:
        with open("/etc/group", "r") as f:
            for line in f:
                if ":" not in line:
                    continue
                cols = line.strip().split(":")
                if len(cols) >= 3:
                    name = cols[0]
                    try:
                        gid = int(cols[2])
                        d[gid] = name
                    except ValueError:
                        continue
    except Exception:
        pass
    return d

PWD_CACHE = parse_passwd()
GRP_CACHE = parse_group()

def resolve_owner_group(path: str) -> Tuple[str, str]:
    """
    Retorna (owner_name, group_name). Usa parsing de /etc/passwd e /etc/group como fonte primária.
    Se não resolvido, retorna UID/GID textual.
    """
    try:
        st = os.stat(path)
    except FileNotFoundError:
        raise
    uid = st.st_uid
    gid = st.st_gid
    owner = PWD_CACHE.get(uid)
    group = GRP_CACHE.get(gid)
    if owner is None:
        owner = f"UID{uid}"
    if group is None:
        group = f"GID{gid}"
    return owner, group

# ---------------------------
# Helpers para aplicar correções
# ---------------------------

def name_to_uid(name: str) -> int:
    # tenta mapear via parsing; se falhar, tenta int() e eventualmente levantar
    for uid, uname in PWD_CACHE.items():
        if uname == name:
            return uid
    # fallback: try to parse numeric
    try:
        return int(name)
    except Exception:
        raise KeyError(f"Usuário {name} não encontrado")

def name_to_gid(name: str) -> int:
    for gid, gname in GRP_CACHE.items():
        if gname == name:
            return gid
    try:
        return int(name)
    except Exception:
        raise KeyError(f"Grupo {name} não encontrado")

def apply_fix(path: str, expected: dict) -> Tuple[bool, str]:
    """
    Aplica chmod e chown conforme esperado.
    Retorna (success, mensagem).
    """
    messages = []
    try:
        # modo
        mode = expected.get("mode")
        if mode is not None:
            os.chmod(path, mode)
            messages.append(f"mode->{oct(mode)}")
        # owner/group
        owner = expected.get("owner")
        group = expected.get("group")
        if owner is not None or group is not None:
            uid = name_to_uid(owner) if owner is not None else os.stat(path).st_uid
            gid = name_to_gid(group) if group is not None else os.stat(path).st_gid
            os.chown(path, uid, gid)
            messages.append(f"owner->{owner}, group->{group}")
        return True, ", ".join(messages)
    except PermissionError:
        return False, "Permissão negada (execute como root)."
    except KeyError as e:
        return False, f"Falha ao resolver usuário/grupo: {e}"
    except FileNotFoundError:
        return False, "Arquivo/diretório não encontrado."
    except Exception as e:
        return False, f"Erro aplicando correção: {e}"

# ---------------------------
# Checagem
# ---------------------------
def check_path(path: str, expected: dict) -> Tuple[bool, list]:
    """
    Retorna (is_ok, list_of_issues)
    """
    issues = []
    if not os.path.exists(path):
        issues.append("INEXISTENTE")
        return False, issues

    st = os.stat(path)
    current_mode = stat.S_IMODE(st.st_mode)
    try:
        owner, group = resolve_owner_group(path)
    except FileNotFoundError:
        issues.append("INEXISTENTE")
        return False, issues

    if "mode" in expected:
        if current_mode != expected["mode"]:
            issues.append(f"Permissão incorreta: {oct(current_mode)} (esperado {oct(expected['mode'])})")
    if "owner" in expected:
        if owner != expected["owner"]:
            issues.append(f"Dono incorreto: {owner} (esperado {expected['owner']})")
    if "group" in expected:
        # se esperado é shadow mas shadow não existe, aceitaremos root como fallback (não marcar)
        exp_group = expected["group"]
        if exp_group not in GRP_CACHE.values():
            # fallback: se o grupo esperado não existe, ignorar checagem de grupo
            pass
        else:
            if group != exp_group:
                issues.append(f"Grupo incorreto: {group} (esperado {exp_group})")
    is_ok = (len(issues) == 0)
    return is_ok, issues

# ---------------------------
# Report generation
# ---------------------------
def generate_report(results: dict, out_json: str = None):
    ts = datetime.datetime.now().isoformat()
    report = {
        "timestamp": ts,
        "results": results
    }
    text = []
    text.append(f"ShadowSec Permission Audit - {ts}\n")
    for path, r in results.items():
        text.append(f"{path}:")
        text.append(f"  exists: {r.get('exists')}")
        text.append(f"  current_mode: {r.get('current_mode')}")
        text.append(f"  current_owner: {r.get('current_owner')}")
        text.append(f"  current_group: {r.get('current_group')}")
        text.append(f"  expected: {r.get('expected')}")
        text.append(f"  ok: {r.get('ok')}")
        if r.get("issues"):
            for it in r["issues"]:
                text.append(f"    - {it}")
        text.append("")
    human = "\n".join(text)
    # save files
    local_json = out_json if out_json else f"shadowsec_permission_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(local_json, "w") as f:
            json.dump(report, f, indent=2)
        write_log_line(f"Relatório JSON salvo em {local_json}")
    except Exception as e:
        write_log_line(f"Falha ao salvar JSON: {e}")
    try:
        human_txt = local_json.replace(".json", ".txt")
        with open(human_txt, "w") as f:
            f.write(human)
        write_log_line(f"Relatório TXT salvo em {human_txt}")
    except Exception as e:
        write_log_line(f"Falha ao salvar TXT: {e}")
    # also print compact human summary
    print("\n=== Sumário ===")
    print(human)

# ---------------------------
# Main flow
# ---------------------------

def main(args):
    auto = args.auto
    results = {}

    log("=== SHADOWSEC PERMISSION AUDIT ===")
    # ensure caches
    global PWD_CACHE, GRP_CACHE
    PWD_CACHE = parse_passwd()
    GRP_CACHE = parse_group()

    for path, expected in SECURE_RULES.items():
        entry = {
            "exists": False,
            "current_mode": None,
            "current_owner": None,
            "current_group": None,
            "expected": expected,
            "ok": False,
            "issues": []
        }
        if not os.path.exists(path):
            entry["issues"].append("inexistente")
            results[path] = entry
            log(f"[WARN] {path} inexistente. Pulando.")
            continue

        st = os.stat(path)
        entry["exists"] = True
        entry["current_mode"] = oct(stat.S_IMODE(st.st_mode))
        try:
            owner, group = resolve_owner_group(path)
        except FileNotFoundError:
            owner, group = ("?", "?")
        entry["current_owner"] = owner
        entry["current_group"] = group

        ok, issues = check_path(path, expected)
        entry["ok"] = ok
        entry["issues"] = issues

        if ok:
            log(f"[OK] {path} está seguro.")
        else:
            log(f"[ALERTA] {path} está inseguro:")
            for it in issues:
                log(f"  - {it}")

            # If group expected does not exist, advise and skip changing group
            expected_group = expected.get("group")
            group_exists = expected_group in GRP_CACHE.values() if expected_group else True

            do_fix = False
            if auto:
                do_fix = True
            else:
                # interactive prompt
                prompt = f" → Deseja aplicar correções em {path}? (s/n): "
                try:
                    resp = input(prompt).strip().lower()
                except KeyboardInterrupt:
                    log("Interrompido pelo usuário.")
                    sys.exit(1)
                if resp.startswith("s"):
                    do_fix = True

            if do_fix:
                # if expected group doesn't exist, fallback logic:
                if expected_group and not group_exists:
                    # choose fallback: 'root' if exists, else keep current group
                    fallback = "root" if "root" in GRP_CACHE.values() else entry["current_group"]
                    log(f"[INFO] Grupo esperado '{expected_group}' não existe — usando fallback '{fallback}'")
                    expected_to_apply = dict(expected)
                    expected_to_apply["group"] = fallback
                else:
                    expected_to_apply = expected

                success, message = apply_fix(path, expected_to_apply)
                if success:
                    log(f"[APLICADO] Correções aplicadas em {path} ({message})")
                    # refresh caches and entry
                    PWD_CACHE = parse_passwd()
                    GRP_CACHE = parse_group()
                    try:
                        owner2, group2 = resolve_owner_group(path)
                    except Exception:
                        owner2, group2 = ("?", "?")
                    entry["current_owner"] = owner2
                    entry["current_group"] = group2
                    entry["current_mode"] = oct(stat.S_IMODE(os.stat(path).st_mode))
                    # re-evaluate
                    ok2, issues2 = check_path(path, expected)
                    entry["ok"] = ok2
                    entry["issues"] = issues2
                    if ok2:
                        log(f"[VERIFICADO] {path} agora está ok.")
                    else:
                        log(f"[AVISO] {path} ainda possui problemas: {issues2}")
                else:
                    log(f"[ERRO] Não foi possível aplicar correção em {path}: {message}")

        results[path] = entry

    # finalize
    generate_report(results)
    log("Scan finalizado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowSec Permission Auditor & Hardener")
    parser.add_argument("--auto", action="store_true", help="Aplica correções automaticamente sem perguntar.")
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        log("Encerrado pelo usuário.")
        sys.exit(1)

