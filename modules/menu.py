#!/usr/bin/env python3
# ================================================================
# ShadowSec Toolkit — Menu Principal
# Autor: Luciano Valadão
# Descrição:
#   Interface interativa para executar módulos do toolkit.
# ================================================================

import os
import sys
from time import sleep

# Importa os módulos internos (ajuste o caminho conforme tua estrutura)
from modules import syscheckup, auditor
from utils import log, run_cmd  # ou: from core import utils, se tua pasta se chama core


# -------------------------
# Funções utilitárias
# -------------------------
def clear():
    os.system("clear" if os.name == "posix" else "cls")


def header():
    clear()
    print("===============================================================")
    print("        🕵️  ShadowSec Toolkit — Painel Principal")
    print("===============================================================")
    print("  [1] Verificação de Sistema (System Checkup)")
    print("  [2] Auditoria Completa (ShadowSec Auditor)")
    print("  [3] Atualizar Dependências")
    print("  [4] Limpar Logs Temporários")
    print("  [0] Sair")
    print("===============================================================")


# -------------------------
# Execução das opções
# -------------------------
def executar_opcao(opcao):
    if opcao == "1":
        utils.log("Iniciando verificação de sistema...")
        syscheckup.run_checkup()
    elif opcao == "2":
        utils.log("Executando auditoria completa...")
        auditor.run_audit()
    elif opcao == "3":
        utils.log("Atualizando dependências dos módulos...")
        os.system("sudo apt update && sudo apt upgrade -y")
    elif opcao == "4":
        utils.log("Limpando logs antigos...")
        log_dir = os.path.expanduser("~/shadows_audit_logs")
        os.system(f"rm -rf {log_dir}/*")
        utils.log(f"Logs limpos em {log_dir}")
    elif opcao == "0":
        utils.log("Encerrando ShadowSec Toolkit...")
        sys.exit(0)
    else:
        print("[!] Opção inválida.")
    input("\nPressione [Enter] para continuar...")


# -------------------------
# Loop principal
# -------------------------
def main_menu():
    while True:
        header()
        opcao = input("Selecione uma opção: ").strip()
        executar_opcao(opcao)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário.")
        sys.exit(0)

