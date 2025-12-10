import json
import webbrowser

# Arquivo JSON de resultados
arquivo_json = "result.json"

# Cores por categoria
cores = {
    "arquivos": "#3498db",       # azul
    "administrativo": "#e67e22", # laranja
    "exposicao": "#e74c3c",      # vermelho
    "imagens": "#9b59b6"         # roxo
}

# Carrega os resultados
with open(arquivo_json, "r", encoding="utf-8") as f:
    dados = json.load(f)

# Gera HTML
html = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>ShadowSec Toolkit - Dork Scanner Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background-color: #2c3e50;
    color: #ecf0f1;
    padding: 20px;
}}
h1 {{
    text-align: center;
    margin-bottom: 30px;
}}
.category {{
    margin-bottom: 30px;
}}
.category h2 {{
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 5px;
}}
.card {{
    background-color: {bg_color};
    padding: 10px 15px;
    margin: 10px 0;
    border-radius: 8px;
}}
.card h3 {{
    margin: 0 0 5px 0;
    font-size: 16px;
}}
.card a {{
    display: block;
    color: #f1c40f;
    text-decoration: none;
    margin-left: 15px;
}}
.card a:hover {{
    text-decoration: underline;
}}
.result-count {{
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 5px;
}}
</style>
</head>
<body>
<h1>ShadowSec Toolkit - Dork Scanner Dashboard</h1>
""".format(bg_color="#34495e")

# Para cada categoria
for categoria, dorks in dados.items():
    html += f'<div class="category">\n<h2>{categoria.upper()}</h2>\n'
    for dork, links in dorks.items():
        count = len(links)
        html += f'<div class="card" style="background-color:{cores.get(categoria,"#34495e")}">'
        html += f'<div class="result-count">{count} resultado(s) encontrado(s)</div>'
        html += f'<h3>{dork}</h3>'
        if links:
            for link in links:
                html += f'<a href="{link}" target="_blank">{link}</a>'
        else:
            html += '<div>Nenhum resultado encontrado</div>'
        html += '</div>'
    html += '</div>'

html += """
</body>
</html>
"""

# Salva arquivo HTML
saida_html = "dashboard_dorks.html"
with open(saida_html, "w", encoding="utf-8") as f:
    f.write(html)

# Abre no navegador
webbrowser.open(saida_html)
