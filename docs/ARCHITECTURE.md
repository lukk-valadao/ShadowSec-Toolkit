# Arquitetura do ShadowSec Toolkit

## 1. Visão Geral

O **ShadowSec Toolkit** é projetado como uma suíte modular de cibersegurança que combina **scripts em Bash** e **módulos em Python**, permitindo auditoria, manutenção e proteção do sistema de forma extensível e automatizada.

A arquitetura prioriza:
- **Modularidade**: Cada função de segurança isolada em um módulo.
- **Interoperabilidade**: Integração entre scripts shell e Python.
- **Expansibilidade**: Facilidade para adicionar novos módulos e funcionalidades.
- **Segurança**: Controles baseados no Common Criteria e análise STRIDE.

---

## 2. Estrutura Macro

```
shadowsec-toolkit/
├── docs/ # Documentação e guias
├── modules/ # Módulos Python principais
├── scripts/ # Scripts Bash (instalação, manutenção, config)
├── toolkit/ # Código comum para integração dos módulos
├── utils/ # Helpers e utilitários genéricos
└── tests/ # Testes automatizados
```

---

## 3. Fluxo de Execução

### 3.1 Auditoria de Sistema
- **Entrada**: Usuário executa `system_checkup.sh`
- **Processo**:
  - Coleta informações do sistema.
  - Chama módulos Python quando necessário (ex.: `net_scan.py`).
  - Gera relatórios para pasta `docs/reports/` (planejado).
- **Saída**: Relatório consolidado de estado do sistema.

---

### 3.2 Verificação de Rede
- **Entrada**: `net_scan.py` (executado isoladamente ou via `system_checkup.sh`)
- **Processo**:
  - Wrapper para Nmap.
  - Identifica hosts ativos e portas abertas.
  - Resultados enviados para log/relatório.

---

### 3.3 Limpeza de Programas Instalados
- **Entrada**: `user-installed-cleaner.sh`
- **Processo**:
  - Lista pacotes instalados pelo usuário.
  - Permite remoção de softwares não necessários.
- **Saída**: Sistema limpo e otimizado.

---

### 3.4 Verificação de Suspensão por Inatividade
- **Entrada**: `idle_suspend_check.py`
- **Processo**:
  - Verifica e ajusta configurações de suspensão automática.
  - Evita acesso não autorizado quando o sistema fica ocioso.

---

## 4. Componentes e Interações

```
+---------------------+
| system_checkup.sh | <---> Módulos Python (net_scan, etc.)
+---------+-----------+
|
v
+---------------------+
| Relatórios / Logs |
+---------------------+

+---------------------+
| user-installed- |
| cleaner.sh |
+---------------------+
```

---

## 5. Segurança na Arquitetura

- Princípio do menor privilégio (root apenas quando necessário).
- Logs centralizados para auditoria.
- Validação de entrada em todos os scripts.
- Planejamento para criptografia de relatórios sensíveis.

---

## 6. Evolução Planejada

- Integração com **OpenVAS** ou sistema próprio de vulnerabilidades.
- Painel web (opcional) para visualizar relatórios.
- Pipeline CI/CD para testes automatizados.
- Expansão dos módulos Python para incluir **detecção de malwares** e **firewall configurator**.

---

