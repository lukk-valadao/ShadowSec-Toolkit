#!/usr/bin/env bash

# ===============================================
# secure_dir.sh
# Hardening de diretório contra execução,
# movimentação lateral e acesso indevido.
#
#Autor: Luciano Valadão
#
# Uso: ./secure_dir.sh /caminho/do/diretorio
# ===============================================

DIR="$1"

if [[ -z "$DIR" ]]; then
    echo "Uso: $0 /caminho/do/diretorio"
    exit 1
fi

if [[ ! -d "$DIR" ]]; then
    echo "Erro: '$DIR' não é um diretório válido."
    exit 1
fi

echo "[+] Aplicando hardening ao diretório: $DIR"

# -----------------------------------------------
# 1. Ajusta proprietários — opcional (descoment.)
# chown -R "$USER":"$USER" "$DIR"
# -----------------------------------------------

# -----------------------------------------------
# 2. Remove execução para grupo e outros
# -----------------------------------------------
find "$DIR" -type f -exec chmod go-rwx {} \;
find "$DIR" -type d -exec chmod go-rwx {} \;

# -----------------------------------------------
# 3. Impede que arquivos novos herdem permissões
# inseguras
# -----------------------------------------------
umask 077

# -----------------------------------------------
# 4. Permite execução *apenas* ao dono
# (caso o diretório contenha scripts internos)
# -----------------------------------------------
find "$DIR" -type f -name "*.sh" -exec chmod u+x {} \;

# -----------------------------------------------
# 5. Remover ACLs, se existirem
# -----------------------------------------------
setfacl -R -b "$DIR" 2>/dev/null

# -----------------------------------------------
# 6. (Opcional) Tornar arquivos imutáveis
# Para impedir substituição por malware:
#   chattr +i arquivo
# -----------------------------------------------
# Descomente para ativar (CUIDADO!!)
# find "$DIR" -type f -exec chattr +i {} \;

echo "[+] Hardening concluído!"

