# 🪄 COSTAR Prompt Generator

Uma aplicação web completa para geração e gerenciamento de prompts estruturados seguindo a metodologia COSTAR.

## ✨ Funcionalidades

- 🎯 **Gerador COSTAR**: Crie prompts estruturados seguindo a metodologia COSTAR (Context, Objective, Style, Tone, Audience, Response)
- 📚 **Templates**: Biblioteca de templates pré-definidos para diferentes categorias
- 💾 **Gerenciamento**: Salve, edite, organize e favorite seus prompts
- 🤖 **Integração AI**: Conecte com Gemini AI para testar prompts
- 📊 **Analytics**: Acompanhe estatísticas de uso e performance
- 👥 **Autenticação**: Sistema completo de usuários com Supabase
- 📱 **Responsivo**: Interface adaptável para desktop e mobile
- 🚀 **Performance**: Sistema de cache com Redis
- 📧 **Notificações**: Sistema de emails para usuários
- 📦 **Backup**: Sistema de backup e restauração de dados

## 🏗️ Arquitetura

### Backend (Python/FastAPI)

- **main.py**: API principal com todas as rotas
- **services/**: Serviços modulares (Supabase, Gemini, Cache, etc.)
- **requirements.txt**: Dependências Python

### Frontend (HTML/CSS/JavaScript)

- **index.html**: Interface web completa e responsiva
- **JavaScript**: SPA com gerenciamento de estado

### Infraestrutura

- **Docker**: Containerização da aplicação
- **Docker Compose**: Orquestração com Redis e Nginx
- **Nginx**: Proxy reverso e serving de arquivos estáticos

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta no Supabase
- API Key do Google Gemini

### 1. Configuração das Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Configure suas chaves no arquivo .env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-publica-aqui
GEMINI_API_KEY=sua-chave-gemini-aqui
```

### 2. Configuração do Banco de Dados

1. Acesse seu projeto no [Supabase](https://supabase.com)
2. Execute o SQL em `database/migrations/001_initial_setup.sql` no SQL Editor
3. Ative a autenticação por email no painel do Supabase

### 3. Executar com Docker (Recomendado)

```bash
# Build e start todos os serviços
docker-compose up --build

# Acesse a aplicação
http://localhost:80
```

### 4. Executar Localmente (Desenvolvimento)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Acesse a aplicação
http://localhost:8000
```

## 📁 Estrutura do Projeto

```
├── main.py                 # API principal FastAPI
├── index.html             # Interface web
├── requirements.txt       # Dependências Python
├── Dockerfile            # Configuração Docker
├── docker-compose.yml    # Orquestração Docker
├── nginx.conf            # Configuração Nginx
├── .env.example          # Exemplo de variáveis de ambiente
│
├── services/             # Serviços modulares
│   ├── supabase_service.py    # Integração Supabase
│   ├── gemini_service.py      # Integração Gemini AI
│   ├── analytics_service.py   # Sistema de analytics
│   ├── cache_service.py       # Sistema de cache
│   ├── notification_service.py # Sistema de notificações
│   └── backup_service.py      # Sistema de backup
│
├── api/                  # Serviços JavaScript (frontend)
│   ├── supabaseService.js     # Cliente Supabase JS
│   └── geminiService.js       # Cliente Gemini JS
│
├── config/               # Configurações
│   └── supabase.js           # Config Supabase frontend
│
└── database/            # Migrações do banco
    └── migrations/
        └── 001_initial_setup.sql
```

## 🎯 Metodologia COSTAR

A metodologia COSTAR estrutura prompts em 6 componentes:

1. **Context** (Contexto): Defina o papel e contexto do assistente
2. **Objective** (Objetivo): Descreva claramente o que você quer alcançar
3. **Style** (Estilo): Especifique o estilo de escrita ou formato
4. **Tone** (Tom): Determine o tom da comunicação
5. **Audience** (Audiência): Identifique o público-alvo
6. **Response** (Resposta): Especifique o formato de resposta desejado

## 🔧 API Endpoints

### Autenticação

- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Prompts

- `GET /api/prompts` - Listar prompts do usuário
- `POST /api/prompts` - Criar novo prompt
- `GET /api/prompts/{id}` - Buscar prompt específico
- `PUT /api/prompts/{id}` - Atualizar prompt
- `DELETE /api/prompts/{id}` - Excluir prompt

### Templates

- `GET /api/templates` - Listar templates públicos
- `POST /api/templates` - Criar template

### Gemini AI

- `POST /api/gemini/generate` - Gerar conteúdo com IA

### Analytics

- `GET /api/analytics/dashboard` - Estatísticas do usuário
- `GET /api/analytics/usage` - Estatísticas de uso

### Utilitários

- `GET /api/health` - Health check
- `POST /api/export/prompts` - Exportar prompts

## 🎨 Interface

A interface web oferece:

- **Gerador**: Formulário intuitivo para criar prompts COSTAR
- **Templates**: Galeria de templates pré-definidos
- **Salvos**: Gerenciamento dos prompts salvos
- **Design Responsivo**: Funciona perfeitamente em desktop e mobile
- **Animações**: Interface fluida com animações CSS

## 🔒 Segurança

- Autenticação JWT com Supabase
- Row Level Security (RLS) no banco
- Validação de dados com Pydantic
- CORS configurado adequadamente
- Sanitização de inputs

## 📊 Performance

- Sistema de cache com Redis
- Lazy loading de componentes
- Compressão de assets
- CDN para bibliotecas externas
- Otimização de consultas SQL

## 🚀 Deploy

### Heroku

```bash
# Instalar Heroku CLI
# Configurar variáveis de ambiente no Heroku
heroku config:set SUPABASE_URL=sua_url
heroku config:set GEMINI_API_KEY=sua_chave

# Deploy
git push heroku main
```

### Vercel/Netlify (Frontend)

- Configure as variáveis de ambiente
- Faça deploy do `index.html` e arquivos estáticos
- Configure a API separadamente

### VPS/Cloud

```bash
# Clone o repositório
git clone <repo-url>
cd gerador-prompt-costar

# Configure .env
# Execute com Docker
docker-compose up -d
```

## 🔧 Desenvolvimento

### Estrutura de Código

- **Backend**: Python/FastAPI com arquitetura modular
- **Frontend**: Vanilla JavaScript com classes ES6
- **Styling**: CSS puro com design responsivo
- **Database**: PostgreSQL via Supabase

### Padrões Utilizados

- Repository Pattern para dados
- Service Layer para lógica de negócio
- MVC no frontend
- RESTful API
- Async/Await em toda aplicação

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte, entre em contato através:

- Email: suporte@costar-generator.com
- Issues: GitHub Issues
- Documentation: [Wiki do Projeto](link-para-wiki)

## 🎉 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Supabase](https://supabase.com/) - Backend as a Service
- [Google Gemini](https://ai.google.dev/) - IA Generativa
- [Redis](https://redis.io/) - Sistema de cache
- Metodologia COSTAR para estruturação de prompts

---

Feito com ❤️ para a comunidade de IA e prompts
