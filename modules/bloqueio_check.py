#!/usr/bin/env python3
# bloqueio_check.py
# ShadowSec Toolkit - Módulo para checar e ajustar bloqueio automático de tela (GNOME)
# Autor: Shadows + Aeris Satana 🦇

import subprocess
import sys
import argparse

def gsettings_get(schema, key):
    try:
        result = subprocess.run(
            ["gsettings", "get", schema, key],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def gsettings_set(schema, key, value):
    try:
        subprocess.run(
            ["gsettings", "set", schema, key, value],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_fix_lock_time(target_minutes, check_only):
    # Schema e chaves que interessam no GNOME:
    # idle-delay (em segundos) - tempo até iniciar o protetor
    # lock-delay (em segundos) - tempo para travar após o protetor
    schema_session = "org.gnome.desktop.session"
    schema_screensaver = "org.gnome.desktop.screensaver"
    key_idle = "idle-delay"
    key_lock = "lock-delay"

    print("🔒 ShadowSec Toolkit - Verificação de bloqueio automático de tela (GNOME)\n")

    idle_raw = gsettings_get(schema_session, key_idle)
    lock_raw = gsettings_get(schema_screensaver, key_lock)

    if idle_raw is None or lock_raw is None:
        print("❌ Erro: Não foi possível acessar as configurações do GNOME (gsettings).")
        sys.exit(1)

    # Valores retornados são do tipo "uint32 N"
    try:
        idle_sec = int(idle_raw.replace("uint32 ", ""))
        lock_sec = int(lock_raw.replace("uint32 ", ""))
    except:
        print("❌ Formato inesperado nos valores de configuração.")
        sys.exit(1)

    target_sec = target_minutes * 60

    print(f"⏳ Tempo atual para ativar protetor (idle-delay): {idle_sec//60} min")
    print(f"🔐 Tempo atual para bloquear tela após protetor (lock-delay): {lock_sec//60} min")
    print(f"🎯 Tempo alvo configurado para bloqueio (lock-delay): {target_minutes} min\n")

    if lock_sec != target_sec:
        if check_only:
            print(f"⚠️ Lock-delay está diferente do alvo ({lock_sec//60} min vs {target_minutes} min), mas não será alterado (--check-only ativo).")
        else:
            print(f"⏳ Ajustando lock-delay para {target_minutes} minutos...")
            success = gsettings_set(schema_screensaver, key_lock, str(target_sec))
            if success:
                print("✅ Lock-delay ajustado com sucesso.")
            else:
                print("❌ Falha ao ajustar lock-delay.")
    else:
        print("✅ Lock-delay já está configurado corretamente.")

    # Opcional: pode também sugerir ajuste do idle-delay para ≤ lock-delay
    if idle_sec > target_sec:
        if check_only:
            print(f"⚠️ idle-delay ({idle_sec//60} min) é maior que lock-delay ({target_minutes} min), considere ajustar.")
        else:
            print(f"⏳ Ajustando idle-delay para {target_minutes} minutos (igual ao lock-delay)...")
            success = gsettings_set(schema_session, key_idle, str(target_sec))
            if success:
                print("✅ idle-delay ajustado com sucesso.")
            else:
                print("❌ Falha ao ajustar idle-delay.")
    else:
        print("✅ idle-delay está adequado (menor ou igual ao lock-delay).")

    print("\n🔄 Para aplicar alterações, pode ser necessário reiniciar a sessão GNOME ou o computador.")

def main():
    parser = argparse.ArgumentParser(description="Verifica e ajusta bloqueio automático de tela GNOME.")
    parser.add_argument("--time", type=int, default=15, help="Tempo para bloqueio em minutos (padrão: 15)")
    parser.add_argument("--check-only", action="store_true", help="Somente verifica, não altera configurações")
    args = parser.parse_args()

    check_and_fix_lock_time(args.time, args.check_only)

if __name__ == "__main__":
    main()

