ShadowSec Toolkit – Dork Scanner
1. Descrição do Módulo
O Dork Scanner é um módulo de reconhecimento OSINT (Open Source Intelligence) do ShadowSec Toolkit, projetado para identificar informações públicas expostas relacionadas a empresas ou pessoas.
O módulo utiliza Google Dorks em conjunto com a SerpAPI, permitindo buscas automatizadas de forma controlada, defensiva e rastreável, evitando scraping direto e bloqueios por parte dos mecanismos de busca.
⚠️ Aviso Legal: este módulo deve ser utilizado exclusivamente com autorização explícita do alvo, para fins de auditoria, defesa e conscientização em segurança da informação.

2. Funcionalidades
2.1 Pesquisa por Empresa
O módulo executa conjuntos de dorks organizados por categoria:
Arquivos expostos
PDFs, DOC/DOCX, XLS/XLSX, PPT/PPTX
CSV, TXT, backups e documentos indexáveis
Administrativo
Páginas de login e painéis administrativos
Portais internos acessíveis publicamente
Diretórios listados (intitle:"index of")
Exposição de informações
Documentos confidenciais
Termos como password, confidential, internal use only
Conteúdo não destinado à distribuição pública
Imagens
JPG, PNG e outros formatos indexados

2.2 Pesquisa por Pessoa
Senhas ou credenciais publicamente indexadas
Currículos (Curriculum Vitae)
Documentos pessoais (ex.: filetype:pdf)

2.3 Características Técnicas
Automatização: múltiplas dorks executadas por categoria
Organização: resultados agrupados por tipo (Arquivos, Administrativo, Exposição, Imagens)
Exportação: geração de arquivo JSON estruturado
Configuração:
Número de resultados por dork configurável
Chave da SerpAPI definida via variável de ambiente ou .env
Reconhecimento passivo: nenhuma exploração ativa é realizada

3. Estrutura de Dados
Exemplo de JSON gerado pelo módulo:
{
  "arquivos": {
    "site:noircode.com.br filetype:pdf": [],
    "site:noircode.com.br filetype:doc": []
  },
  "administrativo": {
    "site:noircode.com.br inurl:login": [],
    "site:noircode.com.br intitle:\"index of\"": [
      "https://www.noircode.com.br/2025/05/google-dorks-guia-completo.html"
    ]
  },
  "exposicao": {
    "\"Noir Code\" confidential": [
      "https://www.beambitx.co/blog/noir-dapps-the-privacy-key/"
    ],
    "\"Noir Code\" password": [
      "https://www.reddit.com/r/IUPUI/comments/1dlcw1h/bypass_code/"
    ]
  },
  "imagens": {
    "site:noircode.com.br filetype:jpg": []
  }
}


4. Integração com o ShadowSec Toolkit
O Dork Scanner pode ser utilizado de forma isolada ou integrada ao ecossistema ShadowSec:
Execução como módulo independente (dork_scanner.py)
Integração com o Dashboard para visualização estruturada dos resultados
Importação de dados por outros módulos para correlação de risco
Integrações previstas com:
net_scan.py – correlação entre serviços expostos e informações públicas
hardening_assistant.py – recomendações de correção baseadas nas exposições detectadas
firewall_configurator.py – bloqueio ou restrição de acessos a áreas expostas

5. Casos de Uso Recomendados
Auditoria de segurança de websites e domínios
Revisão de exposição de informações estratégicas
Testes de conscientização de equipes
Monitoramento contínuo de superfícies públicas
Reconhecimento defensivo em pentests autorizados

6. Boas Práticas
Utilizar somente com autorização formal do alvo
Evitar consultas excessivas para não gerar bloqueios de API
Registrar e versionar os resultados em JSON ou Dashboard
Correlacionar dados com outros módulos para análise completa de risco

7. Dependências e Execução
Python 3.9+
Ambiente virtual (venv) obrigatório
Pacote:
google-search-results
Chave da SerpAPI configurada via variável de ambiente ou .env
A ativação correta do venv é obrigatória para evitar conflitos de dependências em sistemas modernos (PEP 668).

8. Futuras Expansões
Dorks avançadas para redes sociais
Detecção automática de vazamentos de credenciais
Alertas automáticos (e-mail, Slack, webhook)
Integração com feeds de Threat Intelligence
Modo de monitoramento contínuo

⚙️ Criação e ativação do ambiente virtual (venv)
1️⃣ Criar o ambiente virtual
Dentro do diretório do módulo ou do projeto:
python3 -m venv venv

Isso criará um diretório venv/ contendo um ambiente Python isolado.

2️⃣ Ativar o ambiente virtual
Linux / macOS
source venv/bin/activate

Windows (PowerShell)
venv\Scripts\Activate.ps1

Após a ativação, o terminal exibirá algo como:
(venv) usuario@host:~

Isso indica que o ambiente virtual está ativo.

3️⃣ Instalar as dependências
Com o venv ativado:
pip install google-search-results


🔐 Configuração da API (SerpAPI)
O módulo não executa sem uma chave de API configurada.
Definir variável de ambiente (sessão atual)
export SERPAPI_KEY="SUA_CHAVE_AQUI"

Ou definir via arquivo .env (recomendado)
Crie um arquivo .env no diretório do módulo:
SERPAPI_KEY=SUA_CHAVE_AQUI

⚠️ Nunca versionar arquivos .env.
 Adicione ao .gitignore.

▶️ Execução do módulo
Com o venv ativado e a variável configurada:
python3 dork_scanner.py

Se a chave não estiver configurada, o script irá abortar com uma mensagem clara de erro.

🛡️ Boas práticas de segurança
Utilize este módulo apenas em alvos autorizados


Não utilize para coleta massiva ou abusiva


Respeite legislações locais e políticas de uso da API


Este módulo é destinado a estudo, auditoria e defesa
