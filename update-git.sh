#!/bin/bash

# Nome do script: update-git.sh
# Descrição: Atualiza o repositório Git com todas as mudanças feitas no projeto ShadowSec Toolkit

# Diretório do projeto (ajuste se necessário)
PROJECT_DIR="$HOME/Python Proj/shadowsec-toolkit"

# Cores
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RESET='\033[0m'

echo -e "${CYAN}🔁 Atualizando o repositório Git do ShadowSec Toolkit...${RESET}"

# Vai para o diretório do projeto
cd "$PROJECT_DIR" || { echo "❌ Diretório não encontrado!"; exit 1; }

# Verifica alterações
git status

# Adiciona tudo
git add .

# Solicita uma mensagem de commit
read -p "📝 Digite a mensagem do commit: " commit_msg

# Faz o commit
git commit -m "$commit_msg"

# Envia para o GitHub
git push origin main

echo -e "${GREEN}✅ Projeto atualizado com sucesso no GitHub!${RESET}"

