ShadowSec Toolkit – Mini Security Target (ST)
1. Introdução
1.1 Identificação
Produto: ShadowSec Toolkit

Versão: 0.1 (em desenvolvimento)

Autor: Lukk Shadows

Data: 2025-08-04

1.2 Propósito
O ShadowSec Toolkit é uma suíte modular de ferramentas de cibersegurança, criada para auditar, analisar e fortalecer sistemas e redes. Seu objetivo é fornecer recursos práticos para entusiastas e profissionais de segurança, seguindo boas práticas reconhecidas internacionalmente, baseadas no Common Criteria (ISO/IEC 15408).

2. Escopo e Ambiente
2.1 Escopo
Ferramentas de auditoria e hardening para sistemas Linux.

Verificação de segurança de rede local e hosts.

Análise básica de malwares e integridade de arquivos.

Configuração simplificada de firewall e monitoramento de logs.

2.2 Ambiente de Operação
Sistemas operacionais Linux (Debian-based e derivados).

Ambiente de execução: terminal/bash e Python 3.x.

Usuário-alvo: administradores de sistemas, analistas de segurança e estudantes de cibersegurança.

3. Ameaças Mitigadas
T1: Configurações inseguras de sistema e rede.

T2: Acesso não autorizado a dados sensíveis.

T3: Falta de rastreabilidade e auditoria de ações críticas.

T4: Presença de malwares ou arquivos suspeitos.

T5: Vulnerabilidades conhecidas sem detecção ou resposta.

4. Objetivos de Segurança
O1: Identificar e corrigir configurações inseguras (hardening).

O2: Monitorar e auditar atividades para rastreabilidade.

O3: Detectar e alertar sobre malwares ou arquivos suspeitos.

O4: Facilitar configuração de firewall e restrições de acesso.

O5: Gerar relatórios claros e exportáveis para o usuário.

5. Funções de Segurança (Requisitos Funcionais)
Baseadas na Parte 2 do Common Criteria:

Função	Código CC	Descrição
Criptografia de relatórios	FCS_COP	Criptografia para proteger dados de auditoria e relatórios gerados.
Auditoria e geração de logs	FAU_GEN	Geração de registros de eventos importantes para rastreabilidade.
Controle de acesso básico	FIA_UAU	(Futuro) Autenticação para módulos sensíveis ou modo multiusuário.
Teste de integridade	FPT_TST	Verificação de integridade dos módulos e dependências.
Proteção de dados do usuário	FDP_ACC	Garantir que relatórios e backups tenham acesso controlado.

6. Mapeamento dos Módulos do ShadowSec Toolkit
Módulo	Funções de Segurança Relacionadas
system_checkup.sh	FAU_GEN (auditoria), FPT_TST (integridade)
net_scan.py	FAU_GEN (log de varreduras), FDP_ACC (proteção de relatórios)
malware_scan.py	FAU_GEN (log), FPT_TST (verificação de assinaturas)
log_audit.py	FAU_GEN (auditoria), FIA_UAU (futuro: controle de acesso a relatórios)
hardening_assistant.py	FDP_ACC (proteção de configurações), FPT_TST (checagens de estado)
firewall_configurator.py	FDP_ACC (controle de regras), FAU_GEN (log de alterações)
threat_intel_fetcher.py	FAU_GEN (log), FDP_ACC (proteção de dados consultados)

7. Nível de Garantia (EAL)
Nível inicial: EAL1/EAL2 – Avaliação funcional e testes básicos.

Expansão futura: Possível evolução para EAL3/EAL4, com maior formalização e auditorias externas, caso o projeto seja aplicado em ambientes corporativos ou governamentais.

8. Justificativa
Este ST segue a estrutura do Common Criteria para:

Estabelecer boas práticas de segurança desde o início do projeto.

Facilitar auditorias internas e evolução futura para certificação formal.

Garantir que cada módulo seja projetado com funções de segurança claras e rastreáveis.

9. Referências
ISO/IEC 15408 – Common Criteria for Information Technology Security Evaluation.

Common Criteria Portal: https://www.commoncriteriaportal.org
