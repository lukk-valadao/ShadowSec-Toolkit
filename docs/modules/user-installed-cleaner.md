# 🧹 user-installed-cleaner.sh

**Script interativo para listar e remover pacotes instalados manualmente pelo usuário no sistema, com visual Noir.**

---

## 🎯 Objetivo

Este módulo foi desenvolvido para facilitar a visualização e a remoção de programas que foram instalados manualmente pelo usuário, mantendo o sistema mais leve e organizado.

---

## 🚀 Funcionalidades

- Detecta pacotes instalados manualmente (via `apt-mark showmanual`).
- Filtra softwares populares ou utilitários relevantes.
- Exibe o **tamanho de cada pacote** em MB.
- Interface interativa com numeração para facilitar a escolha.
- Visual noir estilizado com cores ANSI (Cyan, Magenta, Vermelho).
- Opção de remoção automatizada com `apt remove --purge`.

---

## 📦 Exemplos de programas identificados

google-chrome-stable - 363.7 MB

libreoffice-writer - 37.3 MB

telegram-desktop - 81.8 MB
...

---

## 🛠️ Como usar

Execute com permissões de root:

```bash
sudo ./modules/user-installed-cleaner.sh
Exemplo de uso

[+] Coletando pacotes instalados manualmente pelo usuário...

[+] Pacotes instalados pelo usuário:
  1) audacity - 22.1 MB
  2) gimp - 12.4 MB
  3) wine - .1 MB
...

Deseja remover algum destes pacotes? (s/n): s
Digite os números dos pacotes a remover (separados por espaço): 2 3

🔒 Aviso
⚠️ Atenção: Este script realiza remoções com apt remove --purge, portanto use com cautela. Sempre revise os pacotes antes de confirmar a exclusão.

📁 Localização
Este módulo encontra-se em:

modules/user-installed-cleaner.sh
👤 Autor
Desenvolvido por Luciano Valadão
Parte integrante do projeto ShadowSec Toolkit
