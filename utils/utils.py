import subprocess
import datetime
import os

# Diretório padrão para logs
LOG_DIR = os.path.expanduser("~/ShadowSec/reports/")
os.makedirs(LOG_DIR, exist_ok=True)

def log(message, module="system"):
    """Cria logs formatados com timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{module.upper()}] {message}"
    print(log_line)

    # Salvar também no arquivo de log global
    log_file = os.path.join(LOG_DIR, "shadowsec.log")
    with open(log_file, "a") as f:
        f.write(log_line + "\n")

def run_cmd(command):
    """Executa comandos shell e retorna stdout + stderr."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        log(f"Erro ao executar comando: {e}", module="utils")
        return "", str(e), 1

