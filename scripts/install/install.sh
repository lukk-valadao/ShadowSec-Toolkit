#!/bin/bash

echo "Iniciando instalação do ShadowSec Toolkit..."

# Atualiza repositórios
sudo apt update

# Instala dependências básicas (ajuste conforme módulos futuros)
sudo apt install -y ufw clamav deborphan

echo "Instalação concluída. Você pode rodar os módulos em 'modules/'."

exit 0
