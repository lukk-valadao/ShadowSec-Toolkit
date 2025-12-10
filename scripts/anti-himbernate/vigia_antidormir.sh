#!/bin/bash
# Luciano Valadão

# Nome do processo que já está rodando
PROCESSO="clamscan"

echo "🌙 Sentinela ativada: impedindo suspensão enquanto '$PROCESSO' estiver rodando..."

# Inibe suspensão enquanto o processo existir
systemd-inhibit --what=handle-lid-switch:sleep:idle \
--who="ShadowSec Toolkit" \
--why="Scan de vírus em andamento" \
bash -c "
    while pgrep -x '$PROCESSO' > /dev/null; do
        echo '⏳ $PROCESSO ainda rodando... mantendo sistema acordado.'
        sleep 30  # verifica a cada 30 segundos
    done
    echo '✅ Processo $PROCESSO finalizado. Sistema liberado para descansar.'
"

