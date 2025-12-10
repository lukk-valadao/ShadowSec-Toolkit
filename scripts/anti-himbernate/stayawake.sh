#!/bin/bash
# Autor Luciano Valadão

# Nome do processo que você quer manter o sistema acordado durante (ex: freshclam ou clamscan)
PROCESSO="clamscan"

echo "🌙 Ativando modo vigilância... impedindo suspensão, hibernação e bloqueio de tela."

# Impede suspensão e hibernação enquanto roda o processo
systemd-inhibit --what=handle-lid-switch:sleep:idle --why="Varredura com ClamAV em andamento" \
bash -c "
    echo '⏳ Iniciando varredura com $PROCESSO...'
    sudo $PROCESSO -r /home/shadows/
    echo '✅ Varredura finalizada!'
"

echo "🌞 Modo normal restaurado. O sistema pode dormir de novo se quiser..."

