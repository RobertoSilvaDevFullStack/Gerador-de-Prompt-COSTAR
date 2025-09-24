# 🤖 Gerador de Prompt COSTAR com IA

Ferramenta avançada para criação e aprimoramento de prompts usando a metodologia COSTAR com integração de Inteligência Artificial via Google Gemini.

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

## 📁 Estrutura Organizada do Projeto

```
├── 📁 frontend/               # Interface Web
│   ├── index.html            # Aplicação principal
│   ├── member-area.html      # Área de membros
│   ├── admin-dashboard.html  # Dashboard administrativo
│   ├── member-area.js        # JavaScript da área de membros
│   └── sw.js                 # Service Worker
├── 📁 services/              # Serviços Backend
│   ├── auth_service.py       # Autenticação e usuários
│   ├── member_area_service.py # Serviços de membros
│   ├── admin_analytics_service.py # Analytics administrativos
│   ├── gemini_service.py     # Integração Gemini
│   ├── analytics_service.py  # Sistema de analytics
│   ├── backup_service.py     # Backup e restauração
│   ├── cache_service.py      # Sistema de cache
│   └── notification_service.py # Notificações
├── 📁 routes/                # Endpoints da API
│   └── member_admin_routes.py # Rotas membros/admin
├── 📁 scripts/               # Scripts e Utilitários
│   ├── start.bat            # Inicialização Windows
│   ├── start.sh             # Inicialização Linux/Mac
│   ├── create_admin_user.py # Criação de usuário admin
│   ├── test_multi_ai.py     # Teste sistema Multi-IA
│   └── validate_api_keys.py # Validação das APIs
├── 📁 data/                  # Dados Locais (JSON)
│   ├── users.json           # Base de usuários
│   ├── member_profiles.json # Perfis de membros
│   ├── saved_templates.json # Templates personalizados
│   ├── api_usage_logs.json  # Logs de uso das APIs
│   ├── ai_usage_stats.json  # Estatísticas das IAs
│   └── user_activities.json # Atividades dos usuários
├── 📁 docs/                  # Documentação
│   ├── README.md            # Documentação detalhada
│   ├── ANALISE_PROJETO.md   # Análise técnica
│   └── CONFIGURAR_GEMINI.md # Setup da API Gemini
├── 📁 docker/                # Containerização
│   ├── docker-compose.yml   # Orquestração
│   └── nginx.conf           # Configuração proxy
├── 📁 database/              # Migrações DB
├── 📁 .vscode/               # Configurações VS Code
│   └── pyrightconfig.json   # Configuração Python
├── main.py                   # Aplicação principal
├── main_demo.py              # Versão demonstração
└── requirements.txt          # Dependências Python
```

## ⚙️ Configuração

1. Configure o arquivo `.env`:

   ```bash
   GEMINI_API_KEY=sua_chave_aqui
   ```

2. Execute o script de inicialização apropriado

3. Acesse http://localhost

## 📚 Documentação

Consulte a pasta `docs/` para documentação completa:

- **Setup:** docs/CONFIGURAR_GEMINI.md
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
