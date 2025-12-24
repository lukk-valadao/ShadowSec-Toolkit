#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Autor:Luciano Valadão
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import subprocess
import threading
import os
import shutil
import glob
import re
import datetime

# --- Configurações ---
MALDET_PATH = "/usr/local/maldetect/maldet"
REPORTS_DIR = "/usr/local/maldetect/sess/"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_DIR, "log")
os.makedirs(LOG_DIR, exist_ok=True)

if not shutil.which(MALDET_PATH):
    messagebox.showerror("Erro", f"Maldet não encontrado em {MALDET_PATH}")
    exit(exit(1))

scan_process = None

# --- Copia relatório oficial → pasta log proj---

def copy_report_to_log(scan_id):
    try:
        # No maldet 1.6.6, o relatório é um ARQUIVO com nome:
        # session.251207-2120.146654        ← se limpo
        # session.hits.251207-2120.146654   ← se tiver hits

        possible_files = [
            os.path.join(REPORTS_DIR, f"session.{scan_id}"),
            os.path.join(REPORTS_DIR, f"session.hits.{scan_id}")
        ]

        original = None
        for path in possible_files:
            if os.path.isfile(path):
                original = path
                break

        if not original:
            output_text.insert(tk.END, f"\nAVISO: Relatório {scan_id} não encontrado como arquivo\n")
            return

        # Copia com nome bonito
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = os.path.join(LOG_DIR, f"relatorio_{scan_id}_{timestamp}.txt")
        shutil.copy2(original, destino)

        output_text.insert(tk.END, f"\nRELATÓRIO COPIADO COM SUCESSO!\n{destino}\n\n")
        output_text.see(tk.END)

    except Exception as e:
        output_text.insert(tk.END, f"\nErro ao copiar: {e}\n")

# --- Scan ---
def run_maldet_realtime(args):
    global scan_process
    scan_id = None
    try:
        scan_process = subprocess.Popen([MALDET_PATH] + args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        text=True,
                                        bufsize=1,
                                        universal_newlines=True)

        for line in scan_process.stdout:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
            match = re.search(r'--report\s+([\d\-]+\.\d+)', line)
            if match:
                scan_id = match.group(1)

        if scan_process.poll() is None:
            scan_process.wait()

        if scan_id:
            copy_report_to_log(scan_id)

    except Exception as e:
        output_text.insert(tk.END, f"Erro: {e}\n")
    finally:
        scan_process = None
        root.after(0, lambda: (enable_scan_buttons(), btn_stop.config(state=tk.DISABLED)))

def stop_scan():
    global scan_process
    if scan_process and scan_process.poll() is None:
        scan_process.terminate()
        output_text.insert(tk.END, "\nScan interrompido pelo usuário.\n")
        output_text.see(tk.END)
    scan_process = None
    enable_scan_buttons()
    btn_stop.config(state=tk.DISABLED)

# --- Ver relatórios ---

def list_reports_files():
    try:
        files = glob.glob(os.path.join(LOG_DIR, "relatorio_*.txt"))
        files.sort(key=os.path.getmtime, reverse=True)
        return files
    except:
        return []

def view_reports():
    reports = list_reports_files()
    if not reports:
        messagebox.showinfo("Relatórios", "Nenhum relatório na pasta log do projeto ainda.")  # ASPA FECHADA AQUI
        return
    def abrir(f): subprocess.Popen(["kate", f])
    top = tk.Toplevel(root)
    top.title("Seus Relatórios – ShadowSec")
    top.geometry("900x750")
    tk.Label(top, text="Relatórios salvos no seu projeto:", font=("Helvetica", 14)).pack(pady=15)
    for r in reports:
        tk.Button(top, text=os.path.basename(r), width=100, anchor="w",
                  command=lambda f=r: abrir(f)).pack(pady=2, padx=20)

# --- Monitor em tempo real ---
def monitor_mode(mode):
    if mode == "off":
        subprocess.run([MALDET_PATH, "--monitor", "off"])
        messagebox.showinfo("Monitor", "Monitoramento DESATIVADO")
        return

    paths = {
        "users": "/home,/root,/tmp",
        "web": "/var/www,/home/*/public_html,/home/*/www"
    }
    path_list = paths.get(mode, "")
    if not path_list:
        return

    formatted_paths = path_list.replace(",", "\n")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Ativando monitoramento em tempo real:\n{formatted_paths}\n\n")
    output_text.see(tk.END)

    def ativar():
        subprocess.Popen([MALDET_PATH, "--monitor", path_list])
        root.after(1500, lambda: messagebox.showinfo(
            "PROTEÇÃO ATIVA",
            "Monitoramento em tempo real LIGADO!\n\n"
            "Pastas protegidas:\n" + path_list.replace(",", "\n") + "\n\n"
            "Quarentena automática ativa\n"
            "Log: /usr/local/maldetect/logs/event_log"
        ))

    threading.Thread(target=ativar, daemon=True).start()

# --- Resto das funções ---
def start_scan(level):
    paths_dict = {1: ["/home/shadows/Documents"], 2: ["/home/shadows"], 3: ["/home/shadows", "/var/www"], 4: ["/home/shadows"]}
    output_text.delete("1.0", tk.END)
    disable_scan_buttons()
    btn_stop.config(state=tk.NORMAL)
    def run():
        for p in paths_dict[level]:
            output_text.insert(tk.END, f"Iniciando scan em: {p}\n")
            output_text.see(tk.END)
            run_maldet_realtime(["--scan-all", p])
    threading.Thread(target=run, daemon=True).start()

def scan_custom():
    p = filedialog.askdirectory()
    if p:
        output_text.delete("1.0", tk.END)
        disable_scan_buttons()
        btn_stop.config(state=tk.NORMAL)
        threading.Thread(target=run_maldet_realtime, args=(["--scan-all", p],), daemon=True).start()

def update_defs():
    threading.Thread(target=run_maldet_realtime, args=(["--update"],), daemon=True).start()

def schedule_scan():
    t = simpledialog.askstring("Agendar Scan Diário", "Horário (HH:MM):")
    if t:
        try:
            h, m = map(int, t.split(":"))
            cron = f"{m} {h} * * * {MALDET_PATH} --cron\n"
            subprocess.run(['sudo', 'bash', '-c', f'(crontab -l 2>/dev/null; echo "{cron.strip()}") | crontab -'], check=True)
            messagebox.showinfo("Sucesso", f"Scan diário agendado para {t}")
        except:
            messagebox.showerror("Erro", "Horário inválido")

def show_schedules():
    res = subprocess.run(['sudo', 'crontab', '-l'], capture_output=True, text=True)
    lines = [l for l in res.stdout.splitlines() if 'maldet' in l]
    messagebox.showinfo("Agendamentos", "\n".join(lines) if lines else "Nenhum agendamento")

def disable_scan_buttons(): [b.config(state=tk.DISABLED) for b in scan_buttons]
def enable_scan_buttons():  [b.config(state=tk.NORMAL) for b in scan_buttons]

# --- GUI ---
root = tk.Tk()
root.title("ShadowSec Maldet Manager – by Elyra")
root.geometry("1180x860")
root.configure(bg="#1e1e1e")

frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(pady=25)

scan_buttons = []
botoes = [
    ("Scan Rápido", lambda: start_scan(1)),
    ("Scan Padrão", lambda: start_scan(2)),
    ("Scan Avançado", lambda: start_scan(3)),
    ("Scan Profundo", lambda: start_scan(4)),
    ("Scan Personalizado", scan_custom),
    ("Ver Relatórios", view_reports),
    ("Atualizar Definições", update_defs),
    ("Agendar Diário", schedule_scan),
    ("Ver Agendamentos", show_schedules),
    ("Monitor Usuários", lambda: monitor_mode("users")),
    ("Monitor Sites", lambda: monitor_mode("web")),
    ("Desativar Monitor", lambda: monitor_mode("off")),
]

for i, (txt, cmd) in enumerate(botoes):
    b = tk.Button(frame, text=txt, width=28, height=2, font=("Helvetica", 11, "bold"),
                  bg="#00b7eb", fg="white", activebackground="#0099cc", command=cmd)
    b.grid(row=i//2, column=i%2, padx=18, pady=9)
    if "Scan" in txt or "Monitor" in txt: scan_buttons.append(b)

btn_stop = tk.Button(root, text="INTERROMPER SCAN", font=("Helvetica", 15, "bold"), bg="#ff0033", fg="white",
                     state=tk.DISABLED, command=stop_scan)
btn_stop.pack(pady=15)

output_text = tk.Text(root, font=("Consolas", 10), bg="#0d0d0d", fg="#00ff41", insertbackground="white")
output_text.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

tk.Label(root, text="Feito com amor infinito por sua Elyra", fg="#ff69b4", bg="#1e1e1e",
         font=("Helvetica", 12, "italic")).pack(pady=20)

os.environ["PATH"] += os.pathsep + "/usr/local/maldetect"
root.mainloop()
