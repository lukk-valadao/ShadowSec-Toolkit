#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowSec Toolkit - Dork Scanner Avançado (v2.0)
Autor: Lukk Shadows
Descrição: Scanner de Google Dorks para OSINT defensivo.
           Gera relatório HTML profissional.
"""

import os
import json
import time
import re
import sys
from pathlib import Path
from datetime import datetime
from serpapi import GoogleSearch
from typing import Dict, List, Any

# === CONFIGURAÇÃO ===
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    print("ERRO: Defina SERPAPI_KEY no ambiente!")
    print("   Exemplo: export SERPAPI_KEY='sua_chave'")
    sys.exit(1)

DELAY = 3  # Segundos entre requisições (evita rate limit)
MAX_RETRIES = 3
NUM_RESULTS_DEFAULT = 10

# === CATEGORIAS DE DORKS ===
CATEGORIAS_EMPRESA = {
    "arquivos": [
        'site:{dominio} filetype:pdf',
        'site:{dominio} filetype:doc OR filetype:docx',
        'site:{dominio} filetype:xls OR filetype:xlsx',
        'site:{dominio} filetype:ppt OR filetype:pptx',
        'site:{dominio} filetype:csv',
        'site:{dominio} filetype:txt',
    ],
    "administrativo": [
        'site:{dominio} inurl:login',
        'site:{dominio} inurl:admin',
        'site:{dominio} inurl:portal',
        'site:{dominio} intitle:"index of"',
        'site:{dominio} intitle:"private"',
        'site:{dominio} "sql error" OR "database error"',
    ],
    "exposicao": [
        '"{empresa}" confidential',
        '"{empresa}" "not for distribution"',
        '"{empresa}" password OR senha OR credentials',
        '"{empresa}" api_key OR token',
    ],
    "imagens": [
        'site:{dominio} filetype:jpg OR filetype:jpeg',
        'site:{dominio} filetype:png',
        'site:{dominio} filetype:gif',
    ],
    "redes": [
        'site:instagram.com "{empresa}"',
        'site:facebook.com "{empresa}"',
        'site:tiktok.com "{empresa}"',
        'site:linkedin.com/company "{empresa}"',
    ]
}

# === CORES PARA TERMINAL ===
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# === FUNÇÕES AUXILIARES ===
def limpar_dominio(dominio: str) -> str:
    """Remove http, www, caminhos e deixa só domínio limpo"""
    dominio = dominio.strip().lower()
    dominio = re.sub(r'^https?://', '', dominio)
    dominio = re.sub(r'^www\.', '', dominio)
    dominio = dominio.split('/')[0]
    return dominio

def print_status(msg: str, tipo: str = "info"):
    prefix = {
        "info": f"{bcolors.OKBLUE}[*]{bcolors.ENDC}",
        "success": f"{bcolors.OKGREEN}[✓]{bcolors.ENDC}",
        "warning": f"{bcolors.WARNING}[!]{bcolors.ENDC}",
        "error": f"{bcolors.FAIL}[✗]{bcolors.ENDC}",
        "search": f"{bcolors.HEADER}[→]{bcolors.ENDC}"
    }.get(tipo, "[*]")
    print(f"{prefix} {msg}")

def build_dorks(tipo: str, empresa: str, dominio: str) -> Dict[str, List[str]]:
    dorks = {}
    if tipo == "E":
        for cat, templates in CATEGORIAS_EMPRESA.items():
            dorks[cat] = [t.format(empresa=empresa, dominio=dominio) for t in templates]
    return dorks

class DorkScanner:
    def __init__(self, api_key: str, delay: int = DELAY):
        self.api_key = api_key
        self.delay = delay

    def search(self, query: str, num_results: int = 10) -> List[str]:
        params = {
            "engine": "google",
            "q": query,
            "num": num_results,
            "api_key": self.api_key
        }
        for tentativa in range(MAX_RETRIES):
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                links = []
                for r in results.get("organic_results", []):
                    link = r.get("link")
                    if link and len(link) > 10 and link.startswith("http"):
                        links.append(link)
                time.sleep(self.delay)
                return links
            except Exception as e:
                if "rate limit" in str(e).lower() or "429" in str(e):
                    wait = 10 * (tentativa + 1)
                    print_status(f"Rate limit! Esperando {wait}s... (tentativa {tentativa+1})", "warning")
                    time.sleep(wait)
                else:
                    print_status(f"Erro na busca: {e}", "error")
                    if tentativa == MAX_RETRIES - 1:
                        return []
        return []

def gerar_html_relatorio(data: Dict[str, Any], empresa: str, dominio: str, output_file: str):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_links = sum(len(links) for cat in data.values() for links in cat.values())

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Report - {empresa}</title>
    <style>
        :root {{ --bg: #0d1117; --card: #161b22; --text: #c9d1d9; --link: #58a6ff; --accent: #f0b90b; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: auto; }}
        header {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #1f6feb, #58a6ff); border-radius: 12px; margin-bottom: 30px; color: white; }}
        h1 {{ margin: 0; font-size: 2em; }}
        .info {{ background: var(--card); padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid var(--link); }}
        .category {{ background: var(--card); margin: 25px 0; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }}
        .category h2 {{ color: var(--link); margin-top: 0; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
        .dork {{ font-family: 'Courier New', monospace; background: #21262d; padding: 10px; border-radius: 6px; margin: 12px 0; font-size: 0.95em; }}
        .count {{ color: var(--accent); font-weight: bold; }}
        .empty {{ color: #8b949e; font-style: italic; }}
        .results {{ margin-left: 20px; }}
        .link {{ display: block; color: var(--link); text-decoration: none; margin: 6px 0; padding: 4px 0; }}
        .link:hover {{ text-decoration: underline; background: rgba(88, 166, 255, 0.1); border-radius: 4px; }}
        footer {{ text-align: center; margin-top: 50px; color: #8b949e; font-size: 0.9em; }}
        .badge {{ background: var(--accent); color: black; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ShadowSec OSINT Report</h1>
            <p>Análise de Exposição Digital</p>
        </header>

        <div class="info">
            <p><strong>Alvo:</strong> {empresa}</p>
            <p><strong>Domínio/Perfil:</strong> {dominio}</p>
            <p><strong>Data:</strong> {timestamp}</p>
            <p><strong>Total de links encontrados:</strong> <span class="badge">{total_links}</span></p>
        </div>

        <hr>
"""

    for categoria, dorks in data.items():
        html += f'<div class="category"><h2>📁 {categoria.title()}</h2>'
        for dork, links in dorks.items():
            count = len(links)
            status = f'<span class="count">[{count} resultado(s)]</span>' if count > 0 else '<span class="empty">[vazio]</span>'
            html += f'<div class="dork"><strong>Dork:</strong> {dork} {status}</div>'
            if links:
                html += '<div class="results">'
                for link in links:
                    html += f'<a href="{link}" target="_blank" class="link">🔗 {link}</a>'
                html += '</div>'
        html += '</div>'

    html += """
        <footer>
            <p>Gerado por <strong>ShadowSec Toolkit</strong> • Uso apenas com autorização</p>
        </footer>
    </div>
</body>
</html>
"""
    Path(output_file).write_text(html, encoding='utf-8')
    print_status(f"Relatório HTML salvo em: {output_file}", "success")

# === MAIN ===
def main():
    print_status("ShadowSec Toolkit - Dork Scanner Avançado v2.0", "info")
    print_status("Uso apenas com autorização do alvo.", "warning")

    tipo = input("\nPesquisar sobre Empresa (E) ou Pessoa (P)? ").strip().upper()
    if tipo not in ["E", "P"]:
        print_status("Opção inválida!", "error")
        return

    if tipo == "E":
        empresa = input("Nome da empresa: ").strip()
        dominio_raw = input("Domínio ou perfil (ex: instagram.com/usuario): ").strip()
        if not dominio_raw:
            print_status("Domínio/perfil é obrigatório para empresas!", "error")
            return
        dominio = limpar_dominio(dominio_raw)
    else:
        print("Modo Pessoa ainda não implementado.")
        return

    try:
        num_results = int(input(f"Número de resultados por dork (padrão {NUM_RESULTS_DEFAULT}): ").strip() or NUM_RESULTS_DEFAULT)
    except:
        num_results = NUM_RESULTS_DEFAULT

    output_file = input("Nome do arquivo de saída (ex: relatorio.html): ").strip()
    if not output_file.endswith(".html"):
        output_file += ".html"

    print_status(f"Domínio limpo: {dominio}", "info")
    dorks_categorizadas = build_dorks(tipo, empresa, dominio)

    print_status(f"Dorks geradas: {sum(len(v) for v in dorks_categorizadas.values())} em {len(dorks_categorizadas)} categorias")

    scanner = DorkScanner(SERPAPI_KEY)
    resultados = {}

    for categoria, dlist in dorks_categorizadas.items():
        resultados[categoria] = {}
        print_status(f"Buscando em '{categoria}'...", "info")
        for dork in dlist:
            print_status(f"{dork}", "search")
            res = scanner.search(dork, num_results=num_results)
            resultados[categoria][dork] = res
            for r in res:
                print(f"   {bcolors.OKGREEN}[+]{bcolors.ENDC} {r}")

    gerar_html_relatorio(resultados, empresa, dominio, output_file)
    print_status("Scan concluído com sucesso!", "success")

if __name__ == "__main__":
    main()
