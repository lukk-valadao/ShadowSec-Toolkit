# Threat Model – ShadowSec Toolkit

## 1. Introdução

Este documento descreve o modelo de ameaças do **ShadowSec Toolkit**, uma suíte modular de cibersegurança para auditoria, limpeza e proteção de sistemas. O objetivo é identificar ameaças potenciais aos módulos e funcionalidades do projeto, classificá-las segundo o modelo **STRIDE** e propor estratégias de mitigação.

---

## 2. Metodologia

O modelo STRIDE classifica ameaças em seis categorias:

- **S**poofing: Falsificação de identidade.
- **T**ampering: Alteração não autorizada de dados.
- **R**epudiation: Ações que não podem ser rastreadas.
- **I**nformation Disclosure: Vazamento de informações.
- **D**enial of Service: Interrupção de serviço.
- **E**levation of Privilege: Obtenção de privilégios indevidos.

---

## 3. Escopo

Inclui os módulos e scripts já implementados e planejados:

- **modules/**
  - `net_scan.py`
  - `bloqueio_check.py`
  - `idle_suspend_check.py`
  - `suspect_hashes.txt` (dados para detecção)
- **scripts/**
  - `system_checkup.sh`
  - `maintenance/user-installed-cleaner.sh`
  - `config/configurar_suspensao.sh`
  - `install/install_clamav.sh`
- **Documentação e dados**
  - `docs/` (incluindo arquivos de configuração e logs gerados)

---

## 4. Ameaças Identificadas por Categoria (STRIDE)

### 4.1 Spoofing
- **Possibilidade**: Um invasor falsifica a origem de pacotes de rede para enganar `net_scan.py`.
- **Impacto**: Resultados incorretos em auditorias de rede; dificuldade de detecção de ativos maliciosos.
- **Mitigação**:
  - Validação de endereços IP detectados.
  - Registro detalhado de logs com timestamp.
  - Uso de ferramentas externas confiáveis (ex.: Nmap autenticado).

---

### 4.2 Tampering
- **Possibilidade**: Alteração do arquivo `suspect_hashes.txt` para ignorar ou incluir hashes falsos.
- **Impacto**: Detecção falha de malwares ou falsos positivos.
- **Mitigação**:
  - Tornar o arquivo somente leitura.
  - Hash de integridade do arquivo (ex.: SHA256 verificado no runtime).
  - Controle de permissões no sistema (chmod).

---

### 4.3 Repudiation
- **Possibilidade**: Usuários executam scripts de limpeza ou auditoria sem geração de logs.
- **Impacto**: Dificuldade para rastrear atividades e diagnosticar incidentes.
- **Mitigação**:
  - Logging obrigatório em todos os módulos críticos.
  - Inclusão de identificação de usuário e data/hora nos registros.

---

### 4.4 Information Disclosure
- **Possibilidade**: Vazamento de resultados do `net_scan.py` ou `system_checkup.sh`.
- **Impacto**: Informações sensíveis sobre topologia de rede e estado do sistema podem ser expostas.
- **Mitigação**:
  - Criptografar relatórios sensíveis (AES/GPG).
  - Controlar permissões de leitura/escrita nas pastas de saída.

---

### 4.5 Denial of Service (DoS)
- **Possibilidade**: Uso abusivo de varreduras de rede ou scripts de manutenção para sobrecarregar o sistema.
- **Impacto**: Lentidão ou indisponibilidade do sistema durante auditorias.
- **Mitigação**:
  - Limitar frequência de execução (cooldowns).
  - Utilizar threads/processos controlados.
  - Configurar limites de recursos (ulimits).

---

### 4.6 Elevation of Privilege
- **Possibilidade**: Scripts que rodam como root podem ser explorados para obter privilégios.
- **Impacto**: Comprometimento total do sistema.
- **Mitigação**:
  - Revisão de código para evitar injeção de comandos.
  - Princípio do menor privilégio (executar como usuário sempre que possível).
  - Validação estrita de entradas e parâmetros.

---

## 5. Conclusão

Este modelo de ameaças fornece uma visão inicial dos riscos do ShadowSec Toolkit e serve como base para priorizar melhorias de segurança e implementação de controles adicionais. Ele deve ser revisado periodicamente conforme novos módulos forem adicionados.

---

## 6. Referências

- [Microsoft STRIDE Threat Model](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [ISO/IEC 15408 – Common Criteria](https://www.commoncriteriaportal.org/)

