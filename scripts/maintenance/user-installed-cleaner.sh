#!/bin/bash

# Cores estilo Noir
RED='\e[91m'
GREEN='\e[92m'
YELLOW='\e[93m'
CYAN='\e[96m'
WHITE='\e[97m'
GRAY='\e[90m'
RESET='\e[0m'

# Verifica se está rodando como root
if [[ "$EUID" -ne 0 ]]; then
  echo -e "${RED}[✗] Este script precisa ser executado como root. Use: sudo $0${RESET}"
  exit 1
fi

echo -e "${CYAN}[+] Coletando pacotes instalados manualmente pelo usuário...${RESET}"

# Lista de pacotes instalados manualmente
manual_pkgs=$(apt-mark showmanual)

# Remove pacotes instalados automaticamente
auto_pkgs=$(apt-mark showauto)
user_pkgs=$(comm -23 <(echo "$manual_pkgs" | sort) <(echo "$auto_pkgs" | sort))

# Filtro com programas de interesse
filtered_pkgs=$(echo "$user_pkgs" | grep -Ei 'chrome|hydrogen|gimp|nmap|ncdu|vlc|kdenlive|audacity|libreoffice|telegram|obs|gparted|htop|yt-dlp|nemo|wine|q4wine|protonvpn|clamav|stellarium|playonlinux' | sort -u)

if [[ -z "$filtered_pkgs" ]]; then
  echo -e "${YELLOW}[!] Nenhum programa relevante identificado entre os pacotes manuais.${RESET}"
  exit 0
fi

echo -e "${GREEN}[+] Pacotes instalados pelo usuário:${RESET}"
count=1
declare -A pkg_map

while IFS= read -r pkg; do
  size=$(dpkg-query -W --showformat='${Installed-Size}\n' "$pkg" 2>/dev/null)
  if [[ -n "$size" ]]; then
    size_mb=$(awk "BEGIN {printf \"%.1f\", $size/1024}")
    [[ "$size_mb" == "0.0" ]] && size_mb="0"
    echo -e "  ${WHITE}$count)${RESET} ${CYAN}$pkg${RESET} - ${YELLOW}${size_mb} MB${RESET}"
  else
    echo -e "  ${WHITE}$count)${RESET} ${CYAN}$pkg${RESET} - ${RED}Tamanho desconhecido${RESET}"
  fi
  pkg_map[$count]=$pkg
  ((count++))
done <<< "$filtered_pkgs"

echo -e "${GRAY}===========================${RESET}"
read -p $'\e[96mDeseja remover algum destes pacotes? (s/n): \e[0m' resposta

if [[ "$resposta" != "s" ]]; then
  echo -e "${GRAY}Ok, nada será removido.${RESET}"
  exit 0
fi

read -p $'\e[96mDigite os números dos pacotes a remover (separados por espaço): \e[0m' -a indices

for i in "${indices[@]}"; do
  prog="${pkg_map[$i]}"
  if [[ -n "$prog" ]]; then
    echo -e "${RED}[!] Removendo $prog...${RESET}"
    apt remove --purge -y "$prog"
  else
    echo -e "${YELLOW}[x] Número inválido: $i${RESET}"
  fi
done

echo -e "${GREEN}[✓] Remoção concluída.${RESET}"
