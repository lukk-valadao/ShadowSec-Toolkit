#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SysCheck-Up v1.0 – Python Edition (com menu estendido)
# Autor: Luciano Valadão
# Objetivo: Portar funcionalidades do SysCheck-Up v1.4.1 para Python (Linux/Windows)

# Importa módulos essenciais do Python
import os # Para interagir com o sistema operacional (limpar tela, etc.)
import subprocess # Para executar comandos shell externos
import platform # Para identificar o sistema operacional (Linux, Windows, etc.)
import shutil # Para operações de alto nível em arquivos (cópia de diretórios, localização de executáveis)
import tempfile # Para obter o diretório temporário do sistema (usado na limpeza)
import datetime # Para manipular datas e horários (usado para logs e timestamps)
import time # Para funções relacionadas a tempo (usado no spinner e pausas)
from pathlib import Path # Para manipulação moderna de caminhos de arquivos (melhor que 'os.path')

# ====== CORES ======
# Define códigos ANSI para colorir o texto no terminal, melhorando a saída visual
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m" # Reset de cor

# ====== LOGGING ======
# Configurações para gerenciamento de logs
BASE_DIR = Path(__file__).resolve().parent # Obtém o diretório base onde o script está
LOG_DIR = BASE_DIR / "Logs" # Define o caminho para a pasta 'Logs'
LOG_DIR.mkdir(parents=True, exist_ok=True) # Cria a pasta 'Logs' se ela não existir
# Cria um nome de arquivo de log com timestamp (AAAA-MM-DD_HH-MM-SS)
LOG_FILE = LOG_DIR / f"syscheckup_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log"

def log(msg):
    """Imprime uma mensagem na tela e a salva no arquivo de log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    # Abre o arquivo de log em modo 'append' (adicionar) e salva a linha
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def pause():
    """Pausa a execução até o usuário pressionar Enter."""
    input("Pressione Enter para continuar...")

def run_cmd(cmd, sudo=False):
    """
    Executa comando shell, captura a saída e o código de retorno.
    Retorna (stdout, stderr, exitcode).
    """
    try:
        # Executa o comando; shell=True permite comandos compostos; text=True decodifica a saída
        proc = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        # Retorna a saída padrão (stdout), erro padrão (stderr) e código de retorno
        return proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except Exception as e:
        # Captura exceções em caso de falha na execução do subprocesso
        return "", str(e), 1

def is_linux():
    """Verifica se o SO é Linux."""
    return platform.system() == "Linux"

def is_windows():
    """Verifica se o SO é Windows."""
    return platform.system() == "Windows"

def spinner(text, duration=0.8):
    """Exibe um spinner de carregamento para feedback visual."""
    chars = "|/-\\"
    end = time.time() + duration
    while time.time() < end:
        for c in chars:
            # Imprime o caractere, limpa a linha e volta ao início (flush=True)
            print(f"\r[{c}] {text}", end="", flush=True)
            time.sleep(0.08)
    print("\r", end="") # Limpa a linha do spinner

# ====== MÓDULOS ======

def atualizacoes():
    """Verifica e aplica atualizações do sistema (apt no Linux, choco no Windows)."""
    log(f"{YELLOW}[1/12] Verificando atualizações do sistema...{NC}")
    if is_linux():
        # Executa apt update, redirecionando a saída para um arquivo temporário e para o console (tee)
        stdout, stderr, rc = run_cmd("sudo apt update 2>&1 | tee /tmp/apt_update.log")

        # Lê o log temporário para análise de erros
        try:
            with open("/tmp/apt_update.log", "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = stdout + "\n" + stderr

        # Lógica para tratar falhas de repositório (404 Not Found, Release file ausente)
        if "does not have a Release file" in content or "404  Not Found" in content:
            log("⚠️  Um ou mais repositórios falharam durante a atualização.")
            opt = input("Deseja desabilitar automaticamente os repositórios inválidos? (1) Sim (2) Não : ")
            if opt.strip() == "1":
                # Itera sobre sources.list e arquivos em sources.list.d
                for p in ["/etc/apt/sources.list"] + list(Path("/etc/apt/sources.list.d").glob("*.list")):
                    try:
                        txt = p.read_text(encoding="utf-8", errors="ignore")
                        if "greenbone" in txt: # Exemplo: desabilita linhas contendo 'greenbone'
                            new = ""
                            for line in txt.splitlines():
                                if "greenbone" in line and not line.strip().startswith("#"):
                                    new += "#DESABILITADO # " + line + "\n" # Comenta a linha
                                else:
                                    new += line + "\n"
                            p.write_text(new, encoding="utf-8")
                            log(f"👉 Repositório {p} desabilitado (linhas contendo 'greenbone').")
                    except Exception as e:
                        log(f"Erro ao processar {p}: {e}")
                log("🔄 Reexecutando atualização com repositórios válidos...")
                run_cmd("sudo apt update | tee -a " + str(LOG_FILE)) # Roda apt update novamente
            else:
                log("👉 Repositórios inválidos foram ignorados.")

        # Conta pacotes para upgrade
        out, err, _ = run_cmd("apt list --upgradable 2>/dev/null | grep -c upgradable")
        try:
            updates = int(out.strip()) if out.strip().isdigit() else 0
        except:
            updates = 0

        if updates > 0:
            log(f"{GREEN}[{updates} pacotes disponíveis para atualização]{NC}")
            # Lista os pacotes disponíveis para upgrade
            out, err, _ = run_cmd("apt list --upgradable 2>/dev/null | grep upgradable || true")
            if out:
                for line in out.splitlines():
                    pretty = line.split(" ")[0]
                    print(f"   • {pretty}")

            # Pergunta qual tipo de upgrade executar
            choice = input("Deseja instalar as atualizações agora? (s/n) ")
            if choice.lower().startswith("s"):
                print("1) Upgrade normal (seguro)")
                print("2) Full-upgrade (atualiza tudo, incluindo substituições de pacotes)")
                upg_choice = input("Escolha o tipo de atualização [1-2]: ")
                if upg_choice.strip() == "2":
                    log("Iniciando full-upgrade...")
                    run_cmd("sudo apt full-upgrade -y | tee -a " + str(LOG_FILE))
                else:
                    log("Iniciando upgrade normal...")
                    run_cmd("sudo apt upgrade -y | tee -a " + str(LOG_FILE))
                log(f"{GREEN}✅ Atualizações concluídas.{NC}")
            else:
                log("Atualização não instalada.")
        else:
            log(f"{GREEN}✅ Sistema já está atualizado.{NC}")
    elif is_windows():
        # Tenta usar o Chocolatey (choco) para atualizar pacotes no Windows
        log("Atualizações (Windows) via Chocolatey (se instalado).")
        if shutil.which("choco"): # Verifica se o choco está no PATH
            out, err, rc = run_cmd("choco upgrade all -y")
            if rc == 0:
                log(f"{GREEN}✅ Atualizações concluídas (choco).{NC}")
            else:
                log(f"{RED}Erro ao atualizar via choco: {err}{NC}")
        else:
            log(f"{YELLOW}Chocolatey não encontrado. Atualizações automáticas não disponíveis.{NC}")
    pause()

def limpeza():
    """Realiza a limpeza de cache, pacotes e lixeira no sistema."""
    log(f"{YELLOW}[2/12] Limpando pacotes e cache...{NC}")
    etapas = 4
    etapa = 0
    if is_linux():
        # Remoção de dependências não mais usadas
        run_cmd("sudo apt autoremove -y | tee -a " + str(LOG_FILE))
        etapa += 1; print_progress_step(etapa, etapas)
        # Limpeza de cache de pacotes baixados
        run_cmd("sudo apt autoclean -y | tee -a " + str(LOG_FILE))
        etapa += 1; print_progress_step(etapa, etapas)
        # Limpeza de logs antigos do systemd
        run_cmd("sudo journalctl --vacuum-time=5d")
        etapa += 1; print_progress_step(etapa, etapas)
        # Esvaziar lixeira
        limpar_lixeira = input("Deseja esvaziar a lixeira? (s/n) ")
        if limpar_lixeira.lower().startswith("s"):
            run_cmd("rm -rf ~/.local/share/Trash/*")
            log("Lixeira esvaziada.")
        else:
            log("Lixeira não foi esvaziada.")
        etapa += 1; print_progress_step(etapa, etapas)
    elif is_windows():
        # Limpa arquivos temporários do sistema
        temp_dir = tempfile.gettempdir()
        etapa += 1; print_progress_step(etapa, etapas)
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
            except Exception:
                pass # Ignora arquivos que não podem ser deletados (em uso)
        etapa += 1; print_progress_step(etapa, etapas)
        log("Arquivos temporários limpos.")
        etapa += 1; print_progress_step(etapa, etapas)
        # Esvaziar lixeira no Windows via PowerShell
        limpar_lixeira = input("Deseja esvaziar a lixeira? (s/n) ")
        if limpar_lixeira.lower().startswith("s"):
            if is_windows():
                run_cmd('powershell -Command "Clear-RecycleBin -Force"')
                log("Lixeira esvaziada.")
            else:
                pass
        etapa += 1; print_progress_step(etapa, etapas)

    log("Limpeza concluída!")
    pause()

def print_progress_step(progress, total):
    """Exibe uma barra de progresso para a função atual."""
    percent = int(progress * 100 / total)
    filled = int(percent / 2)
    empty = 50 - filled
    bar = "#" * filled + " " * empty
    print(f"\r[ {bar} ] {percent}%", end="", flush=True)
    time.sleep(0.05) # Pequena pausa para efeito visual

def firewall():
    """Verifica o status e ajusta o firewall (UFW no Linux, netsh no Windows)."""
    log(f"{YELLOW}[3/12] Verificando status do firewall (UFW/netsh)...{NC}")
    if is_linux():
        if not shutil.which("ufw"): # Se UFW não estiver instalado, instala
            log(f"{RED}UFW não encontrado. Instalando...{NC}")
            run_cmd("sudo apt update -y")
            run_cmd("sudo apt install ufw -y")
            run_cmd("sudo ufw enable")
            log(f"{GREEN}✅ UFW instalado e ativado.{NC}")

        # Mostra o status detalhado do UFW
        out, err, rc = run_cmd("sudo ufw status verbose")
        log(out if out else err)

        # Lista portas e serviços comuns de segurança que devem ser verificados
        portas = {"22":"ssh","25":"exim4","631":"cups"}
        for porta, svc in portas.items():
            # Verifica se a porta está liberada (ALLOW)
            out, err, rc = run_cmd(f"sudo ufw status | grep -E '^{porta} .*ALLOW' || true")
            if out:
                fechar = input(f"[!] Porta {porta} ({svc}) aberta. Deseja fechá-la? (s/n) ")
                if fechar.lower().startswith("s"):
                    # Desabilita o serviço correspondente e nega a porta no firewall
                    run_cmd(f"sudo systemctl stop {svc} || true")
                    run_cmd(f"sudo systemctl disable {svc} || true")
                    run_cmd(f"sudo ufw deny {porta}")
                    log(f"[{porta}] 🔒 Porta fechada e serviço {svc} desativado.")
                else:
                    log(f"[{porta}] 🚪 Mantida aberta.")
            else:
                log(f"[{porta}] Porta não detectada como aberta.")
    elif is_windows():
        # Mostra o status geral do firewall do Windows
        out, err, rc = run_cmd("netsh advfirewall show allprofiles")
        log(out if out else err)
        log("No Windows, recomenda-se revisar as regras via Windows Defender Firewall GUI ou PowerShell.")
    pause()

def clamav_scan():
    """Verifica e executa o scan de vírus (ClamAV no Linux, Defender no Windows)."""
    log(f"{YELLOW}[4/12] Verificando presença do ClamAV...{NC}")
    if is_linux():
        if not shutil.which("clamscan"): # Se ClamAV não está instalado, instala
            log(f"{RED}ClamAV não encontrado. Instalando...{NC}")
            run_cmd("sudo apt install clamav clamav-daemon -y")
            run_cmd("sudo freshclam") # Atualiza as definições de vírus
        choice = input("Deseja executar scan completo em /home? (s/n) ")
        if choice.lower().startswith("s"):
            log("Executando varredura (pode demorar)...")
            # Executa clamscan na /home, exclui dir do Metasploit, toca sino (-bell) e reporta infectados (-i)
            os.system("sudo clamscan -r /home --exclude-dir=/home/*/metasploit-framework --bell -i | tee -a " + str(LOG_FILE))
        else:
            log("Scan pulado.")
    elif is_windows():
        # Tenta atualizar as definições do Windows Defender via MpCmdRun.exe
        out, err, rc = run_cmd(r'%ProgramFiles%\Windows Defender\MpCmdRun.exe -SignatureUpdate')
        if rc == 0:
            log("Definições do Windows Defender atualizadas.")
        else:
            log("Não foi possível atualizar o Defender automaticamente (verifique permissões).")
    pause()

def pacotes_orfaos():
    """Identifica e oferece a remoção de pacotes órfãos (deborphan no Linux)."""
    log(f"{YELLOW}[5/12] Verificando pacotes órfãos...{NC}")
    if is_linux():
        if not shutil.which("deborphan"): # Se deborphan não está instalado, instala
            log("deborphan não encontrado. Instalando...")
            run_cmd("sudo apt install deborphan -y")

        # Roda deborphan para listar pacotes não usados
        out, err, rc = run_cmd("deborphan || true")
        if out.strip():
            log("Pacotes órfãos encontrados:")
            print(out)
            choice = input("Deseja removê-los? (s/n) ")
            if choice.lower().startswith("s"):
                # Remove os pacotes listados pelo deborphan
                run_cmd("sudo apt purge -y " + out.replace("\n"," "))
                log("Orfãos removidos.")
        else:
            log("Nenhum pacote órfão encontrado.")
    elif is_windows():
        log("Operação de pacotes órfãos não aplicável no Windows.")
    pause()

def backup_check():
    """Oferece opções de backup leve ou completo."""
    log(f"{YELLOW}[6/12] Backup...{NC}")
    print("Escolha tipo de backup: 1) Leve 2) Completo 3) Sem backup")
    opt = input("Opção: ").strip()
    if is_linux():
        if opt == "1": # Backup Leve (Documentos, .config e /etc) usando rsync
            dest = str(Path.home() / "backup_leve")
            Path(dest).mkdir(parents=True, exist_ok=True)
            # Usa rsync para cópia eficiente, excluindo cache
            run_cmd(f"rsync -a --exclude='*/.cache' {str(Path.home() / 'Documents')} {dest} || true")
            run_cmd(f"rsync -a --exclude='*/.cache' {str(Path.home() / '.config')} {dest} || true")
            run_cmd(f"rsync -a /etc {dest} || true")
            log(f"Backup leve salvo em: {dest}")
        elif opt == "2": # Backup Completo (/home e /etc) usando rsync com sudo
            dest = str(Path.home() / "backup_completo")
            Path(dest).mkdir(parents=True, exist_ok=True)
            run_cmd(f"sudo rsync -a --exclude='*/.cache' /home {dest} || true")
            run_cmd(f"sudo rsync -a /etc {dest} || true")
            log(f"Backup completo salvo em: {dest}")
        else:
            log("Backup ignorado.")
    elif is_windows():
        dest = input("Caminho destino do backup (ex: D:\\Backups\\syscheck): ").strip()
        if not dest:
            log("Backup ignorado.")
        else:
            Path(dest).mkdir(parents=True, exist_ok=True)
            if opt == "1": # Backup Leve (Documentos e AppData Roaming) usando shutil
                srcs = [str(Path.home() / "Documents"), str(Path.home() / "AppData\\Roaming")]
                for s in srcs:
                    try:
                        shutil.copytree(s, os.path.join(dest, Path(s).name))
                    except Exception:
                        pass
                log(f"Backup leve (Windows) salvo em: {dest}")
            elif opt == "2": # Backup Completo (Tudo na pasta do usuário)
                try:
                    shutil.copytree(str(Path.home()), os.path.join(dest, "home_backup"))
                except Exception as e:
                    log(f"Erro ao copiar: {e}")
                log(f"Backup completo (Windows) salvo em: {dest}")
    pause()

def usuarios_sudo():
    """Lista usuários com privilégios de administrador (sudo no Linux, Administradores no Windows)."""
    log(f"{YELLOW}[7/12] Verificando usuários com privilégios sudo/administradores...{NC}")
    if is_linux():
        # Lista membros do grupo 'sudo'
        out, err, rc = run_cmd("getent group sudo | awk -F: '{print $4}'")
        print(out)
    elif is_windows():
        # Lista membros do grupo local 'Administradores'
        out, err, rc = run_cmd("net localgroup Administradores")
        print(out)
    pause()

def servicos_ativos():
    """Lista serviços ativos e oferece desativar serviços de risco (Blacklist)."""
    log(f"{YELLOW}[8/12] Listando serviços ativos...{NC}")
    # Lista de serviços que podem ser desnecessários ou apresentar risco (ex: servidor de impressão, modems)
    black_list = ["avahi-daemon", "exim4", "cups", "cups-browsed", "ModemManager"]
    if is_linux():
        for svc in black_list:
            out, err, rc = run_cmd(f"systemctl is-active {svc} || true")
            if out.strip() == "active":
                choice = input(f"Serviço {svc} ativo. Deseja desativar? (s/n) ")
                if choice.lower().startswith("s"):
                    # Desativa e para o serviço
                    run_cmd(f"sudo systemctl disable --now {svc}")
                    log(f"{svc} desativado.")
        # Lista todos os serviços em execução
        out, err, rc = run_cmd("systemctl list-units --type=service --state=running")
        print(out)
    elif is_windows():
        # Lista serviços em execução no Windows
        out, err, rc = run_cmd("sc query state= all | findstr /I RUNNING")
        print(out)
    pause()

def espaco_disco():
    """Verifica e exibe o espaço em disco usado e disponível."""
    log(f"{YELLOW}[9/12] Verificando espaço em disco...{NC}")
    if is_linux():
        # Exibe o espaço em formato legível por humanos (df -h)
        out, err, rc = run_cmd("df -h")
        print(out)
    elif is_windows():
        # Usa wmic para obter informações de discos lógicos
        out, err, rc = run_cmd("wmic logicaldisk get size,freespace,caption")
        print(out)
    pause()

def conexoes_rede():
    """Lista conexões de rede ativas (ss no Linux, netstat no Windows)."""
    log(f"{YELLOW}[10/12] Listando conexões de rede ativas...{NC}")
    if is_linux():
        # ss: ferramenta mais moderna para visualizar conexões (socket statistics)
        out, err, rc = run_cmd("ss -tulnp")
        print(out)
    elif is_windows():
        # netstat: lista todas as conexões (com o PID do processo)
        out, err, rc = run_cmd("netstat -ano")
        print(out)
    pause()

def integridade_sistema():
    """Verifica a integridade dos arquivos do sistema (debsums no Linux, sfc no Windows)."""
    log(f"{YELLOW}[11/12] Checando integridade de pacotes/sistema...{NC}")
    if is_linux():
        if not shutil.which("debsums"): # Se debsums não está instalado, instala
            log("debsums não encontrado. Instalando...")
            run_cmd("sudo apt install debsums -y")
        # Roda debsums para verificar arquivos modificados
        out, err, rc = run_cmd("sudo debsums -s || true")
        if out.strip():
            log("Verificações de integridade encontraram problemas (listados abaixo):")
            print(out)
        else:
            log(f"{GREEN}✅ Verificações concluídas (sem erros relatados).{NC}")
    elif is_windows():
        # System File Checker (SFC)
        log("Executando 'sfc /scannow' (pode pedir privilégios de administrador).")
        out, err, rc = run_cmd("sfc /scannow")
        print(out if out else err)
    pause()

def executar_tudo():
    """Executa todos os módulos sequencialmente, pedindo confirmação antes de cada um."""
    log(f"{YELLOW}[12/12] Executar todos os módulos (pergunta s/n para cada)...{NC}")
    # Lista de funções a serem executadas
    funcs = [
        ("Atualizações", atualizacoes),
        ("Limpeza", limpeza),
        ("Firewall", firewall),
        ("Scan ClamAV", clamav_scan),
        ("Pacotes órfãos", pacotes_orfaos),
        ("Backup", backup_check),
        ("Usuários sudo/admin", usuarios_sudo),
        ("Serviços ativos", servicos_ativos),
        ("Espaço em disco", espaco_disco),
        ("Conexões de rede", conexoes_rede),
        ("Integridade do sistema", integridade_sistema),
    ]
    total = len(funcs)
    count = 0
    for name, fn in funcs:
        ans = input(f"Deseja executar '{name}'? (s/n) ")
        if ans.lower().startswith("s"):
            fn() # Chama a função correspondente
        else:
            log(f"{name} pulado.")
        count += 1
        print_progress_global(count, total) # Atualiza barra de progresso total
    log(f"{GREEN}✅ Todos os módulos processados (ou pulados conforme escolha).{NC}")
    pause()

def print_progress_global(progress, total):
    """Exibe a barra de progresso global (usada em executar_tudo)."""
    percent = int(progress * 100 / total)
    filled = int(percent / 2)
    empty = 50 - filled
    bar = "#" * filled + " " * empty
    print(f"\rProgresso total: [ {bar} ] {percent}%", end="", flush=True)
    time.sleep(0.05)

def sair():
    """Exibe mensagem de conclusão e sai do script."""
    log(f"{GREEN}✅ Verificações concluídas. Relatório salvo em: {LOG_FILE}{NC}")
    exit(0)

# ====== MENU PRINCIPAL ======
def menu():
    """Exibe o menu interativo e gerencia as escolhas do usuário."""
    while True:
        # Limpa a tela do terminal (cls para Windows, clear para Linux)
        os.system("cls" if is_windows() else "clear")
        print(f"{GREEN}=== SysCheck-Up v2.1 ==={NC}")
        # Opções do menu...
        print("1) Atualizações do sistema")
        print("2) Limpeza de pacotes e cache")
        print("3) Firewall (UFW / Firewall do sistema)")
        print("4) Scan de vírus (ClamAV / Defender)")
        print("5) Pacotes órfãos")
        print("6) Diretórios de backup")
        print("7) Usuários com privilégios sudo / administradores")
        print("8) Serviços ativos")
        print("9) Espaço em disco")
        print("10) Conexões de rede")
        print("11) Integridade de pacotes do sistema")
        print("12) Executar tudo (com perguntas s/n)")
        print("13) Sair")

        opt = input("Escolha uma opção: ").strip()

        # Mapeamento de opção (string) para a função Python
        mapping = {
            "1": atualizacoes,
            "2": limpeza,
            "3": firewall,
            "4": clamav_scan,
            "5": pacotes_orfaos,
            "6": backup_check,
            "7": usuarios_sudo,
            "8": servicos_ativos,
            "9": espaco_disco,
            "10": conexoes_rede,
            "11": integridade_sistema,
            "12": executar_tudo,
            "13": sair,
        }

        fn = mapping.get(opt) # Busca a função no mapeamento
        if fn:
            fn() # Chama a função encontrada
        else:
            print(f"{RED}Opção inválida{NC}")
            pause()

if __name__ == "__main__":
    # Garante que o menu inicie apenas se o script for executado diretamente
    try:
        menu()
    except KeyboardInterrupt:
        # Captura Ctrl+C para sair de forma limpa
        print("\nSaindo...")
