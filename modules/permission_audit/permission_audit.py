 
#!/usr/bin/env python3
import os
import stat
import subprocess

# Caminhos e permissões recomendadas
SECURE_RULES = {
    "/etc/passwd":      {"mode": 0o644, "owner": "root", "group": "root"},
    "/etc/shadow":      {"mode": 0o640, "owner": "root", "group": "shadow"},
    "/etc/gshadow":     {"mode": 0o640, "owner": "root", "group": "shadow"},
    "/etc/sudoers":     {"mode": 0o440, "owner": "root", "group": "root"},
    "/root":            {"mode": 0o700, "owner": "root", "group": "root"},
    "/tmp":             {"mode": 0o1777, "owner": "root", "group": "root"},
    "/var/log":         {"mode": 0o750, "owner": "root", "group": "adm"},
    "/home":            {"mode": 0o755, "owner": "root", "group": "root"},  # verifica estrutura
}

def get_owner_group(path):
    stat_info = os.stat(path)
    uid = stat_info.st_uid
    gid = stat_info.st_gid
    owner = subprocess.getoutput(f"id -nu {uid}")
    group = subprocess.getoutput(f"id -ng {gid}")
    return owner, group

def check_permissions(path, expected):
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return f"[ERRO] {path} não encontrado."

    current_mode = stat.S_IMODE(st.st_mode)
    owner, group = get_owner_group(path)

    status = []

    if current_mode != expected["mode"]:
        status.append(f"  - Permissão incorreta: {oct(current_mode)} (esperado {oct(expected['mode'])})")

    if owner != expected["owner"]:
        status.append(f"  - Dono incorreto: {owner} (esperado {expected['owner']})")

    if group != expected["group"]:
        status.append(f"  - Grupo incorreto: {group} (esperado {expected['group']})")

    if not status:
        return f"[OK] {path} está seguro."

    alert = f"[ALERTA] {path} está inseguro:\n" + "\n".join(status)
    return alert

def apply_fix(path, expected):
    os.chmod(path, expected["mode"])
    subprocess.run(["chown", f"{expected['owner']}:{expected['group']}", path])
    print(f"[APLICADO] Correções aplicadas em {path}")

def main():
    print("=== SHADOWSEC PERMISSION AUDIT ===\n")

    for path, expected in SECURE_RULES.items():
        result = check_permissions(path, expected)
        print(result)

        if "[ALERTA]" in result:
            resp = input(f" → Deseja aplicar correções em {path}? (s/n): ").lower()
            if resp.startswith("s"):
                try:
                    apply_fix(path, expected)
                except PermissionError:
                    print(f"[ERRO] Permissão negada para corrigir {path}. Execute como root.")
            print()

if __name__ == "__main__":
    main()
