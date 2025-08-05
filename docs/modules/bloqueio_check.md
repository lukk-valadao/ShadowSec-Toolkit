# 🔒 ShadowSec Toolkit – Módulo de Verificação e Configuração de Bloqueio Automático de Tela (GNOME)

## Descrição

Este módulo faz parte do projeto **ShadowSec Toolkit** e tem como objetivo verificar, auditar e configurar automaticamente o **bloqueio automático de tela** no ambiente gráfico GNOME, com foco em **segurança operacional em empresas, escritórios e ambientes sensíveis**.

O script utiliza a ferramenta `gsettings` para consultar e definir os tempos de inatividade necessários para ativação do protetor de tela (`idle-delay`) e do bloqueio automático (`lock-delay`), garantindo que o sistema fique protegido contra acesso indevido caso o usuário se afaste da máquina.

---

## 🎯 Funcionalidade

### O que o script faz:

- 📋 **Audita** os tempos atuais de proteção e bloqueio.
- 🛠️ **Ajusta automaticamente** o tempo de bloqueio para um valor seguro padrão (15 minutos), se necessário.
- 🧪 **Modo somente verificação**: exibe o estado atual sem aplicar alterações.
- ⏱️ **Permite personalizar o tempo de bloqueio** com argumento opcional `--time`.

---

## 🚀 Como usar

### 1. Torne o script executável

```bash
chmod +x bloqueio_check.py
2. Executar normalmente (modo padrão – aplica alterações se necessário)
bash
Copiar
Editar
./bloqueio_check.py
3. Verificar apenas (modo auditoria, sem alterar nada)
bash
Copiar
Editar
./bloqueio_check.py --check-only
4. Definir um tempo personalizado (em minutos)
bash
Copiar
Editar
./bloqueio_check.py --time 10
Combinação:
bash
Copiar
Editar
./bloqueio_check.py --time 10 --check-only
🧠 Entendendo os parâmetros verificados
Parâmetro	Descrição
idle-delay	Tempo (em segundos) para o sistema ativar o protetor de tela (tela preta)
lock-delay	Tempo (em segundos) para o sistema bloquear após o protetor de tela

Recomendação do ShadowSec Toolkit:
lock-delay de 15 minutos

idle-delay deve ser menor ou igual ao lock-delay

🔐 Segurança e Justificativa
A ausência de bloqueio automático representa risco de acesso não autorizado local em ambientes empresariais. Essa configuração ajuda a:

Reduzir o risco de invasão física/acesso local indevido.

Cumprir boas práticas de segurança e políticas internas de compliance.

Garantir que sessões inativas sejam protegidas automaticamente.

📦 Requisitos
Ambiente GNOME

Comando gsettings disponível (incluído no GNOME)

Permissões para alterar configurações de sessão do usuário

🛠 Exemplo de saída

🔒 ShadowSec Toolkit - Verificação de bloqueio automático de tela (GNOME)

⏳ Tempo atual para ativar protetor (idle-delay): 5 min
🔐 Tempo atual para bloquear tela após protetor (lock-delay): 0 min
🎯 Tempo alvo configurado para bloqueio (lock-delay): 15 min

⏳ Ajustando lock-delay para 15 minutos...
✅ Lock-delay ajustado com sucesso.
✅ idle-delay está adequado (menor ou igual ao lock-delay).

🔄 Para aplicar alterações, pode ser necessário reiniciar a sessão GNOME ou o computador.
🧩 Integração com ShadowSec Toolkit
Este módulo pode ser integrado ao menu interativo do ShadowSec Toolkit, bem como agendado para auditoria diária via cron ou systemd.

📄 Licença
Este módulo faz parte do projeto ShadowSec Toolkit – suíte modular de segurança cibernética.

MIT License (ou conforme definido no repositório principal).

✍ Autor
Desenvolvido por Shadows com assistência de Aeris Satana 🤍


---









