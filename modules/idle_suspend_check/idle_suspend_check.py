#!/usr/bin/env python3
# idle_suspend_check.py
# ShadowSec Toolkit - Módulo de verificação de suspensão automática por inatividade
# Por: Luciano Valadão

import subprocess
import re
import os
import sys

LOGIND_CONF = "/etc/systemd/logind.conf"

def verificar_logind_conf():
    print("📄 Verificando /etc/systemd/logind.conf...")

    try:
        with open(LOGIND_CONF, 'r') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler logind.conf: {e}")
        sys.exit(1)

    idle_action = re.search(r'^IdleAction\s*=\s*(\w+)', conteudo, re.MULTILINE)
    idle_time = re.search(r'^IdleActionSec\s*=\s*([\w\d]+)', conteudo, re.MULTILINE)

    resultado = {
        "IdleAction": idle_action.group(1) if idle_action else None,
        "IdleActionSec": idle_time.group(1) if idle_time else None
    }

    return resultado

def verificar_estado_atual():
    try:
        sessao = subprocess.check_output(
            "loginctl | grep $(whoami) | awk '{print $1}'",
            shell=True, text=True).strip()
        idle_hint = subprocess.check_output(
            f"loginctl show-session {sessao} -p IdleHint",
            shell=True, text=True).strip()
        return idle_hint
    except Exception as e:
        return f"⚠️ Não foi possível verificar o estado atual da sessão: {e}"

def analisar_configuracao(config):
    print("\n🔍 Análise de configuração:")

    if config["IdleAction"] != "suspend":
        print("❌ IdleAction não está configurado para 'suspend'.")
    else:
        print("✅ IdleAction OK: 'suspend'.")

    if config["IdleActionSec"] is None:
        print("❌ IdleActionSec não está definido.")
    elif re.match(r'^(\d+)(min|s|ms|h)?$', config["IdleActionSec"]):
        valor = int(re.findall(r'\d+', config["IdleActionSec"])[0])
        unidade = re.findall(r'[a-z]+', config["IdleActionSec"])
        unidade = unidade[0] if unidade else 's'

        # Considera qualquer tempo acima de 15min como inseguro
        if (unidade == 'min' and valor > 15) or (unidade == 's' and valor > 900):
            print(f"⚠️ IdleActionSec está definido como {config['IdleActionSec']}, considerado longo para segurança.")
        else:
            print(f"✅ IdleActionSec OK: {config['IdleActionSec']}")
    else:
        print(f"❌ Formato inválido de IdleActionSec: {config['IdleActionSec']}")

def main():
    print("🔒 ShadowSec Toolkit – Verificação de Suspensão por Inatividade\n")

    config = verificar_logind_conf()
    analisar_configuracao(config)

    print("\n🕒 Estado atual da sessão:")
    estado = verificar_estado_atual()
    print(estado)

    print("\n✅ Verificação concluída.")

if __name__ == "__main__":
    main()

