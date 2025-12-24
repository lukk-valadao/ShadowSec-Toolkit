#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShadowSec Toolkit - Dork Scanner Avançado
Autor: Lukk Shadows
Descrição:
    Scanner de Google Dorks inteligente para pesquisa defensiva (OSINT).
    ⚠️ Uso apenas com autorização do alvo.
    Requer SerpAPI Key.
"""

import json
import time
from serpapi import GoogleSearch

# === SUA SERPAPI KEY AQUI ===
SERPAPI_KEY = "5f2271187dfdf8e6583e2148e513653706477c971415b70d7ed2fe4208b5b4f8"

# Categorias de dorks por tipo
CATEGORIAS_EMPRESA = {
    "arquivos": [
        'site:{dominio} filetype:pdf',
        'site:{dominio} filetype:doc',
        'site:{dominio} filetype:xls',
        'site:{dominio} filetype:ppt',
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
        '"{empresa}" password',
    ],
    "imagens": [
        'site:{dominio} filetype:jpg',
        'site:{dominio} filetype:png'
    ]
}

CATEGORIAS_PESSOA = {
    "arquivos": [
        '"{pessoa}" filetype:pdf',
        '"{pessoa}" filetype:doc'
    ],
    "exposicao": [
        '"{pessoa}" password',
        '"{pessoa}" curriculum vitae'
    ],
    "redes_sociais": [
        '"{pessoa}" site:linkedin.com',
        '"{pessoa}" site:github.com',
        '"{pessoa}" site:facebook.com',
        '"{pessoa}" site:twitter.com',
        '"{pessoa}" site:instagram.com'
    ],
    "imagens": [
        '"{pessoa}" filetype:jpg',
        '"{pessoa}" filetype:png'
    ]
}


def build_dorks(tipo, empresa="", dominio="", pessoas=[]):
    dorks = {}
    if tipo == "E":
        for categoria, templates in CATEGORIAS_EMPRESA.items():
            dorks[categoria] = [t.format(empresa=empresa, dominio=dominio, pessoa="") for t in templates]
    elif tipo == "P":
        for categoria, templates in CATEGORIAS_PESSOA.items():
            dorks[categoria] = []
            for t in templates:
                for p in pessoas:
                    dorks[categoria].append(t.format(pessoa=p.strip(), empresa="", dominio=""))
    return dorks


class DorkScanner:
    def __init__(self, api_key=SERPAPI_KEY, delay=2):
        self.api_key = api_key
        self.delay = delay

    def search(self, query, num_results=10):
        params = {
            "engine": "google",
            "q": query,
            "num": num_results,
            "api_key": self.api_key
        }
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            links = [r["link"] for r in results.get("organic_results", [])]
            links = [l for l in links if len(l) > 10]
            time.sleep(self.delay)
            return links
        except Exception as e:
            print(f"[!] Erro na busca: {e}")
            return []


def main():
    print("=== ShadowSec Toolkit - Dork Scanner Avançado ===")
    tipo = input("Pesquisar sobre Empresa (E) ou Pessoa (P)? ").strip().upper()

    empresa = ""
    dominio = ""
    pessoas = []

    if tipo == "E":
        empresa = input("Nome da empresa: ").strip()
        dominio = input("Domínio principal da empresa (ex: empresa.com): ").strip()
    elif tipo == "P":
        pessoas = input("Nomes das pessoas (separados por vírgula): ").split(",")

    num_results = input("Número de resultados por dork (padrão 10): ").strip()
    num_results = int(num_results) if num_results.isdigit() else 10

    output_file = input("Nome do arquivo de saída (padrão: resultados.json): ").strip()
    output_file = output_file if output_file else "resultados.json"

    dorks_categorizadas = build_dorks(tipo, empresa, dominio, pessoas)
    print("\n[*] Dorks geradas por categoria:")
    for cat, dlist in dorks_categorizadas.items():
        print(f"  - {cat}: {len(dlist)} dorks")

    scanner = DorkScanner()
    resultados = {}

    for categoria, dlist in dorks_categorizadas.items():
        resultados[categoria] = {}
        for dork in dlist:
            print(f"[*] Buscando ({categoria}): {dork}")
            res = scanner.search(dork, num_results=num_results)
            resultados[categoria][dork] = res
            for r in res:
                print(f"  [+] {r}")

    with open(output_file, "w") as f:
        json.dump(resultados, f, indent=4)

    print(f"\n[✓] Resultados salvos em {output_file}")


if __name__ == "__main__":
    main()
