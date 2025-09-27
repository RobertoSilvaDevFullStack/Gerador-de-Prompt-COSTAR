# 🤖 Gerador de Prompt COSTAR com Multi-IA

Ferramenta avançada para criação e aprimoramento de prompts usando a metodologia COSTAR com integração de **múltiplas IAs** e **sistema de failover automático**.

## 🌟 Novidades v2.0 - Sistema Multi-IA

- 🤖 **5 Provedores**: Groq, Gemini, HuggingFace, Cohere, Together AI
- 🔄 **Failover Automático**: Troca automática quando uma IA falha
- ⚡ **Balanceamento Inteligente**: Usa sempre a IA mais rápida disponível
- 📊 **Monitoramento Real**: Status e performance das IAs em tempo real
- 🛡️ **99.9% Disponibilidade**: Sistema resiliente e confiável
- 💰 **Otimização de Quotas**: Maximiza uso de limites gratuitos

## 🚀 Início Rápido

### Windows

```bash
cd scripts
.\start.bat
```

### Linux/Mac

```bash
cd scripts
./start.sh
```

### Acesso

- **Frontend:** http://localhost
- **API:** http://localhost:8000
- **Documentação:** http://localhost:8000/docs

## 📁 Estrutura do Projeto

```
├── 📁 config/                 # Configurações centralizadas
│   ├── __init__.py           # Módulo Python
│   ├── supabase_config.py    # Config Supabase
│   └── paths.py              # Caminhos do projeto
├── 📁 data/                   # Dados da aplicação
│   ├── users.json            # Dados de usuários
│   ├── saved_templates.json  # Templates salvos
│   └── system_metrics.json   # Métricas do sistema
├── 📁 docs/                   # Documentação completa
│   ├── README.md             # Documentação detalhada
│   ├── ANALISE_PROJETO.md    # Análise técnica
│   ├── CONFIGURAR_GEMINI.md  # Setup da API Gemini
│   ├── IMPLEMENTACAO_CONCLUIDA.md  # Status da implementação
│   └── STRUCTURE.md          # Estrutura do projeto
├── 📁 frontend/              # Interface web
│   ├── index.html           # Aplicação principal
│   ├── member-area.html     # Painel de membros
│   ├── admin-dashboard.html # Dashboard admin
│   └── sw.js                # Service Worker
├── 📁 logs/                  # Logs do sistema
│   ├── server.log           # Log do servidor
│   └── server_output.log    # Output do servidor
├── 📁 routes/               # Rotas da API
│   ├── member_admin_routes.py  # Rotas de membros e admin
│   └── status_routes.py     # Status da aplicação
├── 📁 scripts/              # Scripts de automação
│   ├── start.bat           # Inicialização Windows
│   ├── start.sh            # Inicialização Linux/Mac
│   └── setup_costar_users_table.py  # Setup DB
├── 📁 services/             # Serviços backend
│   ├── multi_ai_service.py  # Sistema Multi-IA
│   ├── supabase_auth_service.py  # Autenticação
│   ├── member_area_service.py     # Área de membros
│   └── admin_analytics_service.py # Analytics admin
├── 📁 tests/               # Testes automatizados
│   └── test_*.py           # Arquivos de teste
├── 📁 tools/               # Ferramentas e utilitários
│   ├── batch/              # Scripts batch Windows
│   │   ├── debug_jwt.bat   # Debug JWT
│   │   └── test_complete.bat  # Teste completo
│   └── testing/            # Scripts de teste Python
│       ├── test_members.py # Teste de membros
│       └── test_quick.py   # Teste rápido
├── 📁 docker/              # Containerização
│   ├── docker-compose.yml  # Orquestração
│   └── Dockerfile.demo     # Imagem da aplicação
├── main.py                 # Servidor principal
├── main_demo.py            # Servidor de demonstração
├── requirements.txt        # Dependências Python
└── .env                    # Variáveis de ambiente
```

## ⚙️ Configuração Multi-IA

### 🎯 **Setup Recomendado** (Máxima Disponibilidade)

Configure pelo menos 3 APIs no arquivo `.env`:

```bash
# Sistema Multi-IA
GROQ_API_KEY=gsk_xxxxxx          # Principal (rápido)
GEMINI_API_KEY=AIzaSyxxxxxx      # Backup primário
HUGGINGFACE_API_KEY=hf_xxxxxx    # Backup secundário
COHERE_API_KEY=xxxxxx            # Emergência
TOGETHER_API_KEY=xxxxxx          # Qualidade especial
```

### 🥈 **Setup Mínimo** (Funcional)

Configure pelo menos 2 APIs:

```bash
GROQ_API_KEY=gsk_xxxxxx          # Principal
GEMINI_API_KEY=AIzaSyxxxxxx      # Backup
```

📖 **Guia completo**: Veja `docs/CONFIGURAR_MULTIPLAS_IAS.md` para obter todas as chaves

## � Monitoramento do Sistema

### Status das IAs

```bash
curl https://seu-projeto.vercel.app/api/ai/status
```

### Teste de Conectividade

```bash
curl https://seu-projeto.vercel.app/api/ai/test
```

## �📚 Documentação

Consulte a pasta `docs/` para documentação completa:

- **🔑 Multi-IA:** docs/CONFIGURAR_MULTIPLAS_IAS.md ⭐
- **Setup Gemini:** docs/CONFIGURAR_GEMINI.md
- **Análise:** docs/ANALISE_PROJETO.md
- **Melhorias:** docs/MELHORIAS_IA.md

## 🛠️ Tecnologias

- **Backend:** FastAPI + Python
- **Frontend:** HTML5 + JavaScript
- **IA:** Google Gemini API
- **Container:** Docker + Nginx
- **Cache:** Redis

## 📄 Licença

MIT License - Veja docs/ para mais detalhes.
