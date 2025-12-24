# 🛜 ShadowSec Rootkit Scan v1.0 — Descrição Técnica de Funcionamento🛡️

![OS](https://img.shields.io/badge/OS-Linux-blueviolet.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Security](https://img.shields.io/badge/focus-cybersecurity-red.svg)
![Category](https://img.shields.io/badge/type-rootkit%20scanner-darkred.svg)
![Usage](https://img.shields.io/badge/usage-defensive%20only-important.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Visão Geral

O **ShadowSec Rootkit Scan** é uma ferramenta de auditoria e detecção de rootkits para sistemas Linux, desenvolvida com foco em **análise forense, detecção comportamental e verificação cruzada de fontes do sistema**. Diferente de scanners puramente baseados em assinaturas, o ShadowSec busca **inconsistências operacionais**, técnicas clássicas de ocultação e mecanismos de persistência utilizados por rootkits em userland e kernel space.

O scanner opera obrigatoriamente com privilégios de **root**, pois depende de acesso completo a `/proc`, módulos do kernel, portas de rede e diretórios sensíveis do sistema.

Ao final da execução, são gerados dois relatórios:

* **RAW**: saída bruta, ideal para análise forense, ingestão em SIEM ou arquivamento.
* **READABLE**: versão formatada e quebrada para leitura humana.

---

## Arquitetura Geral

A ferramenta é composta por:

* Funções auxiliares de execução e formatação
* Conjunto modular de verificações independentes
* Menu interativo com três modos de operação
* Mecanismo de geração de relatórios com timestamp

Cada verificação retorna uma **string estruturada**, que é agregada ao relatório final, garantindo consistência e rastreabilidade.

---

## Funções Auxiliares

### `run(cmd)`

Executa comandos do sistema via `subprocess.check_output`.

**Características técnicas:**

* Execução via shell
* Captura apenas de `stdout`
* `stderr` descartado para evitar ruído
* Em caso de falha, retorna string vazia

Essa função é a base de toda a coleta de dados do sistema.

---

### `save_readable_report()`

Responsável por gerar os relatórios finais.

**Funcionamento:**

* Gera timestamp no formato `YYYY-MM-DD_HH-MM-SS`
* Cria dois arquivos distintos
* O relatório READABLE utiliza `textwrap` para quebrar linhas acima de 120 caracteres

Esse processo melhora significativamente a leitura de saídas extensas como `ss`, `lsof` e `ps`.

---

## Verificações Executadas

### 1. Processos root suspeitos (`check_root_processes`)

Analisa processos executados pelo usuário `root` cujo binário está localizado em diretórios não convencionais:

* `/tmp`
* `/var/tmp`
* `/dev/shm`
* `/home`
* `.cache`

**Ferramentas utilizadas:**

* `ps`
* `awk`

**Objetivo:**
Detectar execução maliciosa a partir de diretórios temporários ou voláteis, técnica comum em implantes pós-exploração.

---

### 2. Binários deletados em execução (`check_deleted_binaries`)

Verifica processos cujo executável foi removido do disco, mas continua residente em memória.

**Ferramentas utilizadas:**

* Leitura simbólica de `/proc/*/exe`
* `ls`
* `grep`

**Objetivo:**
Identificar técnicas de *fileless persistence* e execução furtiva.

---

### 3. Processos em diretórios suspeitos (`check_suspicious_dirs`)

Busca processos em execução a partir de caminhos ocultos, temporários ou fora do padrão do sistema.

**Ferramentas utilizadas:**

* `ps`
* `grep -E`

**Objetivo:**
Detectar malwares que evitam `/usr/bin`, `/bin` ou `/sbin` para reduzir visibilidade.

---

### 4. Portas abertas e serviços ativos (`check_open_ports`)

Enumera portas abertas e associa processos a serviços de rede.

**Ferramentas utilizadas:**

* `ss -tulpn` (principal)
* `netstat -tulpn` (fallback)
* `lsof -i`

**Objetivo:**
Detectar backdoors, bind shells, listeners não documentados e serviços ocultos.

---

### 5. Processos ocultos (`check_hidden_processes`)

Realiza uma verificação cruzada entre três fontes independentes:

* `ps`
* `/proc`
* `lsof`

Diferenças entre essas listas indicam possível ocultação ativa.

**Objetivo:**
Detectar rootkits que manipulam syscalls ou estruturas internas para esconder processos.

---

### 6. Módulos suspeitos do kernel (`check_kernel_modules`)

Analisa módulos carregados no kernel em busca de nomes associados a rootkits conhecidos.

**Ferramentas utilizadas:**

* `lsmod`

**Palavras-chave analisadas:**

* `diamorphine`
* `reptile`
* `rootkit`
* `xhide`
* `suterusu`

**Objetivo:**
Detectar LKMs maliciosos responsáveis por ocultação avançada.

---

### 7. Persistência via systemd (`check_systemd_persistence`)

Enumera serviços de inicialização automática:

* `/etc/systemd/system/`
* `~/.config/systemd/user/`

**Ferramentas utilizadas:**

* `ls -la`

**Objetivo:**
Detectar backdoors configurados para execução persistente no boot.

---

### 8. Integridade de pacotes (`check_debsums`)

Verifica se arquivos pertencentes a pacotes Debian foram alterados.

**Ferramenta externa:**

* `debsums`

**Objetivo:**
Detectar substituição de binários legítimos por versões trojanizadas.

---

### 9. Hooks LD_PRELOAD (`check_ld_preload`)

Procura definições de `LD_PRELOAD` em `/etc`.

**Objetivo:**
Detectar hijacking de bibliotecas compartilhadas para interceptação de funções.

---

### 10. Hashes de binários críticos (`check_essential_binaries`)

Calcula MD5 de binários essenciais como:

* `ls`, `ps`, `bash`, `sudo`, `ssh`, `login`

**Ferramenta utilizada:**

* `md5sum`

**Objetivo:**
Permitir comparação manual ou automatizada com hashes conhecidos.

---

### 11. Verificação de scanners externos (`check_rkhunter_chkrootkit`)

Detecta a presença de ferramentas clássicas de detecção.

**Ferramentas externas:**

* `rkhunter`
* `chkrootkit`

**Objetivo:**
Complementar a análise com scanners baseados em assinatura.

---

### 12. Execução de scanners externos (`run_external_scanners`)

Caso disponíveis, executa:

* `rkhunter --check --sk --cronjob`
* `chkrootkit`

Os resultados são exibidos no terminal e registrados no relatório.

---

## Modos de Operação

### Scan Rápido

Triagem inicial focada em:

* Processos suspeitos
* Binários deletados
* Diretórios anômalos
* Portas abertas
* Módulos do kernel

---

### Scan Completo

Auditoria profunda incluindo:

* Persistência
* Integridade de pacotes
* Hooks
* Binários críticos
* Scanners externos

---

### Caça Fantasma

Modo especializado em:

* Processos ocultos
* Serviços de rede furtivos

---

## Considerações de Segurança

* O script **não altera o sistema**, apenas coleta informações
* Deve ser executado em ambiente confiável
* Ideal para resposta a incidentes, hardening e auditorias

---

## Licença e Uso

Ferramenta destinada a fins educacionais, defensivos e auditoria autorizada.

Uso indevido é de responsabilidade exclusiva do operador.

2025.
