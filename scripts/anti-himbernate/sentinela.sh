#!/bin/bash

# Módulo Sentinela – ShadowSec Toolkit
# Impede que o sistema hiberne/suspenda enquanto um processo estiver ativo
# Autor: Luciano Valadão

PROCESSO="$1"

if [ -z "$PROCESSO" ]; then
    echo "Uso: $0 <nome_do_processo>"
    exit 1
fi

echo "🌙 Sentinela ativada: impedindo suspensão enquanto '$PROCESSO' estiver rodando..."

systemd-inhibit --what=handle-lid-switch:sleep:idle \
--who="ShadowSec Toolkit" \
--why="Processo $PROCESSO em andamento" \
bash -c "
    while pgrep -x \"$PROCESSO\" > /dev/null; do
        echo '⏳ '$PROCESSO' ainda rodando... mantendo sistema acordado.'
        sleep 30
    done
    echo '✅ Processo '$PROCESSO' finalizado. Sistema liberado para descansar.'
"

