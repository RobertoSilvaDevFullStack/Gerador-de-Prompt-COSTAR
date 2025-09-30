# 🎯 COSTAR Generator - Sistema Completo de Geração de Prompts

**Plataforma profissional** para criação e gerenciamento de prompts COSTAR com **autenticação Supabase**, **dashboard administrativo** e **sistema multi-IA** integrado.

## ✨ Sistema Completo v3.0

### 🔐 **Autenticação & Usuários**

- ✅ **Login/Logout** com Supabase Auth + JWT
- ✅ **Sistema de Membros** com área exclusiva
- ✅ **Dashboard Admin** com métricas em tempo real
- ✅ **Alteração de senhas** e gerenciamento de perfil
- ✅ **Row Level Security** (RLS) no banco de dados

### 🤖 **Sistema Multi-IA Avançado**

- ✅ **5 Provedores**: Groq, Gemini, HuggingFace, Cohere, Together AI
- ✅ **Failover Automático**: Troca inteligente entre IAs
- ✅ **Balanceamento de Carga**: Otimização automática de performance
- ✅ **Monitoramento Real**: Status e health checks das APIs
- ✅ **Sistema de Quotas**: Maximização de limites gratuitos

### 📊 **Gerenciamento de Dados**

- ✅ **Banco Supabase** com 6 tabelas estruturadas
- ✅ **Sistema de Templates** pré-configurados
- ✅ **Histórico de Prompts** por usuário
- ✅ **Analytics e Métricas** em tempo real
- ✅ **Modo Demo** como fallback automático

## 🚀 Início Rápido

### **Opção 1: Modo Demo (Imediato)**

```bash
python main.py
# Acesso: http://localhost:8000
```

### **Opção 2: Modo Completo (Com Supabase)**

```bash
# 1. Configurar Supabase (veja docs/CONFIGURAR_SUPABASE.md)
# 2. Executar deploy do banco
python scripts/deploy_supabase_schema.py
# 3. Iniciar servidor
python main.py
```

### **Acesso ao Sistema**

- **🏠 Frontend:** http://localhost:8000
- **👥 Área de Membros:** http://localhost:8000/member-area.html
- **🔧 Dashboard Admin:** http://localhost:8000/admin-dashboard.html
- **📚 API Docs:** http://localhost:8000/docs
- **🩺 Health Check:** http://localhost:8000/api/status/health

## 📁 Estrutura do Projeto

```
COSTAR-Generator/
├── � config/                    # Configurações centralizadas
│   ├── supabase_config.py       # Config Supabase + validação
│   └── paths.py                 # Caminhos do sistema
├── �️ database/                  # Schema e scripts de banco
│   ├── schema.sql               # 6 tabelas com RLS
│   ├── deploy_clean.sql         # Deploy limpo
│   └── migrations/              # Migrações
├── � data/                      # Dados da aplicação
│   ├── users.json               # Demo users
│   ├── saved_templates.json     # Templates pré-configurados
│   ├── system_metrics.json      # Métricas do sistema
│   └── member_analytics.json    # Analytics de membros
├── 🌐 frontend/                  # Interface web completa
│   ├── index.html               # Homepage com login
│   ├── member-area.html         # Área de membros
│   ├── admin-dashboard.html     # Dashboard administrativo
│   └── sw.js                    # Service Worker
├── � routes/                    # APIs REST organizadas
│   ├── member_admin_routes.py   # Rotas de membros e admin
│   └── status_routes.py         # Health checks e status
├── ⚙️ services/                  # Lógica de negócio
│   ├── integrated_data_service.py    # Orquestrador principal
│   ├── supabase_base_service.py      # Conexão Supabase
│   ├── multi_ai_service.py           # Sistema Multi-IA
│   ├── supabase_auth_service.py      # Autenticação
│   ├── member_area_service.py        # Área de membros
│   └── admin_analytics_service.py    # Analytics admin
├── 🧪 scripts/                   # Automação e testes
│   ├── deploy_supabase_schema.py     # Deploy automático do banco
│   ├── test_supabase_setup.py        # Diagnóstico completo
│   ├── test_endpoints.py             # Teste de APIs
│   ├── test_multi_ai.py              # Teste das IAs
│   └── create_admin_user_supabase.py # Criar usuário admin
├── 📚 docs/                      # Documentação detalhada
│   ├── CONFIGURAR_SUPABASE.md        # Setup Supabase passo-a-passo
│   ├── IMPLEMENTACAO_CONCLUIDA.md    # Status da implementação
│   ├── MIGRACAO_SUPABASE_COMPLETA.md # Guia de migração
│   └── CONFIGURAR_MULTIPLAS_IAS.md   # Setup das IAs
├── main.py                       # 🚀 Servidor principal
├── main_demo.py                  # 🧪 Servidor de demo
├── requirements.txt              # Dependências Python
├── .env.example                  # Template de configuração
└── vercel.json                   # Config para deploy Vercel
```

## 🛠️ Configuração Completa

### 1️⃣ **Configuração Básica (Modo Demo)**

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar em modo demo
python main.py
```

### 2️⃣ **Configuração Supabase (Modo Produção)**

**Passo 1 - Criar projeto Supabase:**

1. Acesse https://supabase.com
2. Crie um novo projeto
3. Copie as credenciais

**Passo 2 - Configurar .env:**

```bash
cp .env.example .env
# Edite .env com suas credenciais:
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_publica
SUPABASE_SERVICE_ROLE_KEY=sua_chave_admin
```

**Passo 3 - Deploy do banco:**

```bash
python scripts/deploy_supabase_schema.py
```

**Passo 4 - Criar usuário admin:**

```bash
python scripts/create_admin_user_supabase.py
```

### 3️⃣ **Configuração Multi-IA (Opcional)**

```bash
# Adicione ao .env pelo menos 2 APIs:
GROQ_API_KEY=gsk_xxxxxx          # Recomendado (rápido)
GEMINI_API_KEY=AIzaSyxxxxxx      # Recomendado (confiável)
HUGGINGFACE_API_KEY=hf_xxxxxx    # Opcional
COHERE_API_KEY=xxxxxx            # Opcional
TOGETHER_API_KEY=xxxxxx          # Opcional
```

📖 **Guia detalhado:** `docs/CONFIGURAR_MULTIPLAS_IAS.md`

## Endpoints da API

### **Sistema & Saúde**

- `GET /api/status/health` - Status geral
- `GET /api/status/database` - Status do banco
- `GET /api/status/features` - Funcionalidades ativas
- `POST /api/status/test-connection` - Teste completo

### **Autenticação**

- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/logout` - Logout
- `POST /api/auth/register` - Registro (se habilitado)

### **Área de Membros**

- `GET /api/members/prompts` - Prompts do usuário
- `POST /api/members/prompts` - Salvar prompt
- `GET /api/members/templates` - Templates disponíveis
- `PUT /api/members/profile` - Atualizar perfil

### **Dashboard Admin**

- `GET /api/admin/users` - Listar usuários
- `GET /api/admin/analytics` - Métricas do sistema
- `GET /api/admin/logs` - Logs de atividade

### **Sistema Multi-IA**

- `GET /api/ai/status` - Status das IAs
- `POST /api/ai/generate` - Gerar texto
- `GET /api/ai/test` - Teste de conectividade

## 🧪 Teste e Diagnóstico

### **Verificação de Sistema**

```bash
# Teste completo do sistema
python scripts/test_endpoints.py

# Diagnóstico Supabase
python scripts/test_supabase_setup.py

# Teste das IAs
python scripts/test_multi_ai.py
```

### **Status em Tempo Real**

```bash
# Via curl
curl http://localhost:8000/api/status/health

# Via browser
http://localhost:8000/api/status/features
```

## 🚀 Deploy e Produção

### **Vercel (Recomendado)**

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Configurar variáveis de ambiente na dashboard Vercel
```

### **Docker**

```bash
# Modo demo
docker-compose -f docker/docker-compose.yml up

# Modo produção com Supabase
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up
```

### **Servidor Traditional**

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar com gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🛠️ Tecnologias Utilizadas

### **Backend**

- **FastAPI** - Framework web moderno e rápido
- **Supabase** - Backend-as-a-Service com PostgreSQL
- **JWT** - Autenticação stateless
- **Pydantic** - Validação de dados

### **Frontend**

- **HTML5/CSS3/JavaScript** - Interface moderna
- **Bootstrap 5** - Framework CSS responsivo
- **Service Worker** - Funcionalidade offline

### **Banco de Dados**

- **PostgreSQL** (via Supabase)
- **Row Level Security** - Segurança por linha
- **6 Tabelas Estruturadas** - Schema completo

### **Sistema Multi-IA**

- **Groq** - LLaMA models (rápido)
- **Google Gemini** - Modelo avançado
- **HuggingFace** - Open source models
- **Cohere** - Modelos de comando
- **Together AI** - Modelos especializados

## 📚 Documentação Detalhada

### **Guias de Configuração**

- 📖 [Configurar Supabase](docs/CONFIGURAR_SUPABASE.md) - Setup completo do banco
- 🤖 [Configurar Multi-IA](docs/CONFIGURAR_MULTIPLAS_IAS.md) - Setup dos provedores de IA
- 🔧 [Implementação Completa](docs/IMPLEMENTACAO_CONCLUIDA.md) - Status do projeto
- 🚀 [Migração Supabase](docs/MIGRACAO_SUPABASE_COMPLETA.md) - Guia de migração

### **Documentação Técnica**

- 🏗️ [Arquitetura Supabase](docs/ARQUITETURA_SUPABASE.md) - Design do sistema
- 📊 [Análise do Projeto](docs/ANALISE_PROJETO.md) - Visão técnica
- 🔍 [Melhorias IA](docs/MELHORIAS_IA.md) - Otimizações do sistema

## 🎯 Status do Projeto

### ✅ **Implementado e Funcionando**

- 🔐 Sistema de autenticação completo (Supabase + JWT)
- 👥 Área de membros com geração de prompts COSTAR
- 🔧 Dashboard administrativo com analytics reais
- 🤖 Sistema Multi-IA com 5 provedores
- 📊 Banco de dados estruturado com RLS
- 🛡️ Sistema de failover automático
- 📈 Monitoramento e health checks
- 🌐 Interface web responsiva

### 🚧 **Em Desenvolvimento**

- 📧 Sistema de notificações por email
- 💳 Integração com sistemas de pagamento
- 🔄 Sincronização automática entre dispositivos
- 📱 Aplicativo mobile (PWA avançado)

### 🎯 **Roadmap Futuro**

- 🌍 Internacionalização (i18n)
- 🎨 Temas personalizáveis
- 🔌 Plugin system para extensões
- 📊 Analytics avançados com BigQuery

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

### **Problemas Comuns**

- 🔧 [FAQ - Solução de Problemas](docs/FAQ.md)
- 🐛 [Issues no GitHub](https://github.com/RobertoSilvaDevFullStack/Gerador-de-Prompt-COSTAR/issues)

### **Contato**

- 📧 Email: [seu-email@exemplo.com]
- 💬 Discord: [Link do servidor]
- 🐦 Twitter: [@seu_usuario]

---

## 🎉 Status: **SISTEMA COMPLETO E FUNCIONAL** ✅

O COSTAR Generator está em pleno funcionamento com todas as funcionalidades principais implementadas e testadas. Sistema pronto para produção!

**Última atualização:** Setembro 2025 | **Versão:** 3.0.0
