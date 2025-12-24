 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowSec Toolkit - Dork Scanner Avançado (v2.0)
SEM CHAVE NO CÓDIGO → SEGURANÇA MÁXIMA
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

# === CHAVE VIA VARIÁVEL DE AMBIENTE (SEGURA!) ===
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    print("\nERRO: SERPAPI_KEY não definida!")
    print("   Rode antes: export SERPAPI_KEY='sua_nova_chave'")
    print("   Crie uma nova em: https://serpapi.com/dashboard\n")
    sys.exit(1)

# === CONFIGURAÇÕES ===
DELAY = 3
MAX_RETRIES = 3
NUM_RESULTS_DEFAULT = 10

# === CATEGORIAS ===
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
        'site:{dominio} "sql error"',
    ],
    "exposicao": [
        '"{empresa}" confidential',
        '"{empresa}" "not for distribution"',
        '"{empresa}" password OR senha',
    ],
    "imagens": [
        'site:{dominio} filetype:jpg OR filetype:jpeg',
        'site:{dominio} filetype:png',
    ],
    "redes": [
        'site:instagram.com "{empresa}"',
        'site:facebook.com "{empresa}"',
    ]
}

# === CORES ===
class C:
    BLUE = '\033[94m'; GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'; END = '\033[0m'; BOLD = '\033[1m'

def p(msg, tipo="info"):
    icons = {"info": "[*]", "ok": "[+]", "warn": "[!]", "err": "[x]", "search": "[→]"}
    colors = {"info": C.BLUE, "ok": C.GREEN, "warn": C.YELLOW, "err": C.RED, "search": C.BLUE}
    print(f"{colors.get(tipo, '')}{icons.get(tipo, '[*]')} {msg}{C.END}")

def limpar_dominio(d):
    d = d.strip().lower()
    d = re.sub(r'^https?://', '', d)
    d = re.sub(r'^www\.', '', d)

    # CORREÇÃO: Mantém o caminho completo para Instagram, Facebook, TikTok
    if any(platform in d for platform in ['instagram.com/', 'facebook.com/', 'tiktok.com/']):
        # Remove apenas parâmetros (?...) e barra final
        return d.split('?')[0].rstrip('/')

    # Para sites normais, mantém só o domínio
    return d.split('/')[0]

def build_dorks(empresa, dominio):
    return {cat: [t.format(empresa=empresa, dominio=dominio) for t in tmpls]
            for cat, tmpls in CATEGORIAS_EMPRESA.items()}

class Scanner:
    def __init__(self):
        self.delay = DELAY

    def search(self, q, n=10):
        for _ in range(MAX_RETRIES):
            try:
                res = GoogleSearch({"q": q, "num": n, "api_key": SERPAPI_KEY}).get_dict()
                links = [r["link"] for r in res.get("organic_results", []) if "link" in r and len(r["link"]) > 10]
                time.sleep(self.delay)
                return links
            except Exception as e:
                if "429" in str(e):
                    p("Rate limit! Esperando 15s...", "warn")
                    time.sleep(15)
                else:
                    p(f"Erro: {e}", "err")
        return []

def gerar_html(data, empresa, dominio, arquivo):
    total = sum(len(v) for c in data.values() for v in c.values())
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>OSINT - {empresa}</title>
<style>
    body {{font-family: system-ui; background:#0d1117; color:#c9d1d9; padding:20px;}}
    .card {{background:#161b22; padding:20px; margin:15px 0; border-radius:10px; border:1px solid #30363d;}}
    h1, h2 {{color:#58a6ff;}}
    .dork {{background:#21262d; padding:10px; border-radius:6px; font-family:monospace; margin:10px 0;}}
    .link {{color:#58a6ff; display:block; margin:5px 0;}}
    .link:hover {{text-decoration:underline;}}
    .badge {{background:#f0b90b; color:black; padding:3px 8px; border-radius:12px; font-size:0.8em;}}
</style></head><body>
<div style="max-width:1000px;margin:auto">
<h1>ShadowSec OSINT Report</h1>
<div class="card"><strong>Alvo:</strong> {empresa}<br><strong>Perfil:</strong> {dominio}<br><strong>Data:</strong> {timestamp}<br><strong>Total:</strong> <span class="badge">{total}</span></div>
"""
    for cat, dorks in data.items():
        html += f'<div class="card"><h2>{cat.title()}</h2>'
        for dork, links in dorks.items():
            count = len(links)
            status = f'<strong style="color:#f0b90b">[{count}]</strong>' if count else '<em style="color:#777">[vazio]</em>'
            html += f'<div class="dork">Dork: {dork} {status}</div>'
            if links:
                for l in links:
                    html += f'<a href="{l}" target="_blank" class="link">Link: {l}</a>'
        html += '</div>'
    html += "</div></body></html>"
    Path(arquivo).write_text(html, encoding='utf-8')
    p(f"Relatório salvo: {arquivo}", "ok")

# === MAIN ===
def main():
    p("ShadowSec Dork Scanner v2.0", "info")
    p("Use apenas com autorização!", "warn")

    tipo = input("\n(E)mpresa ou (P)essoa? ").strip().upper()
    if tipo != "E":
        p("Modo Pessoa em desenvolvimento.", "warn")
        return

    empresa = input("Nome da empresa: ").strip()
    dom_raw = input("Domínio/perfil (ex: instagram.com/user): ").strip()
    if not dom_raw:
        p("Domínio obrigatório!", "err")
        return
    dominio = limpar_dominio(dom_raw)

    try:
        n = int(input(f"Resultados por dork [{NUM_RESULTS_DEFAULT}]: ") or NUM_RESULTS_DEFAULT)
    except:
        n = NUM_RESULTS_DEFAULT

    out = input("Arquivo de saída (ex: rel.html): ").strip()
    if not out.endswith(".html"):
        out += ".html"

    p(f"Domínio limpo: {dominio}")
    dorks = build_dorks(empresa, dominio)
    p(f"{sum(len(v) for v in dorks.values())} dorks em {len(dorks)} categorias")

    scanner = Scanner()
    resultados = {}

    for cat, lista in dorks.items():
        resultados[cat] = {}
        p(f"Buscando: {cat}...", "info")
        for d in lista:
            p(d, "search")
            res = scanner.search(d, n)
            resultados[cat][d] = res
            for r in res:
                print(f"   {C.GREEN}[+]{C.END} {r}")

    gerar_html(resultados, empresa, dominio, out)
    p("Scan concluído!", "ok")

if __name__ == "__main__":
    main()
