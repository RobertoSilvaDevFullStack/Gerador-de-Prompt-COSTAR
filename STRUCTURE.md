# 📁 Estrutura do Projeto COSTAR

## 🏗️ **Arquitetura Organizada**

Esta documentação descreve a nova estrutura organizacional do projeto.

## 📂 **Estrutura de Pastas**

```
📁 Gerador-de-Prompt-COSTAR/
├── 📄 main.py                 # Aplicação principal
├── 📄 main_demo.py           # Versão demo da aplicação  
├── 📄 requirements.txt       # Dependências Python
├── 📄 README.md             # Documentação principal
├── 📄 .env.example          # Exemplo de configuração
├── 📄 vercel.json           # Configuração de deploy
├── 📄 pyrightconfig.json    # Configuração Python/Pylance
├── 📄 .gitignore           # Arquivos ignorados pelo Git
│
├── 📁 frontend/            # Interface web
│   ├── index.html         # Página principal
│   ├── admin-dashboard.html
│   └── admin-dashboard.js
│
├── 📁 services/           # Serviços do backend
│   ├── multi_ai_service.py
│   ├── gemini_service.py
│   ├── auth_service.py
│   └── ...
│
├── 📁 routes/            # Rotas da API
│   └── member_admin_routes.py
│
├── 📁 data/             # Dados da aplicação
│   ├── users.json
│   ├── saved_prompts.json
│   └── ...
│
├── 📁 scripts/          # Scripts utilitários
│   ├── create_admin_user.py
│   ├── validate_api_keys.py
│   ├── start.bat
│   └── ...
│
├── 📁 docs/            # Documentação técnica
│   ├── README.md
│   ├── CONFIGURAR_GEMINI.md
│   └── ...
│
├── 📁 docker/          # Containers
│   ├── Dockerfile.demo
│   └── docker-compose.yml
│
├── 📁 database/        # Banco de dados
│   └── migrations/
│
├── 📁 tests/           # 🧪 Testes (DESENVOLVIMENTO)
│   ├── test_*.py
│   ├── test_*.html
│   └── README.md
│
├── 📁 debug/           # 🔍 Debug (DESENVOLVIMENTO)
│   ├── debug_*.py
│   └── README.md
│
└── 📁 logs/            # 📋 Logs (DESENVOLVIMENTO)
    ├── CORREÇOES_DASHBOARD.md
    └── README.md
```

## 🎯 **Categorias de Arquivos**

### ✅ **PRODUÇÃO** (essenciais):
- **Raiz**: Apenas arquivos essenciais para funcionamento
- **frontend/**: Interface completa do usuário
- **services/**: Lógica de negócio e integrações
- **routes/**: Endpoints da API
- **data/**: Dados persistentes da aplicação
- **docs/**: Documentação oficial

### 🛠️ **DESENVOLVIMENTO** (organizados):
- **tests/**: Todos os arquivos de teste
- **debug/**: Scripts de diagnóstico e debug
- **logs/**: Histórico de correções e logs
- **scripts/**: Ferramentas e automações

### ⚙️ **INFRAESTRUTURA**:
- **docker/**: Configurações de container
- **database/**: Esquemas e migrações

## 🚀 **Como Executar**

### 🖥️ **Servidor Principal**:
```bash
python main.py
# ou
python main_demo.py  # versão demo
```

### 🧪 **Executar Testes**:
```bash
python tests/test_prompt_generation.py
python tests/test_analysis_endpoint.py
```

### 🔍 **Debug**:
```bash
python debug/debug_multi_ai.py
python debug/debug_gemini.py
```

### 📦 **Scripts**:
```bash
python scripts/create_admin_user.py
python scripts/validate_api_keys.py
```

## ⚠️ **Importante**

- **Produção**: Use apenas arquivos da raiz e pastas principais
- **Desenvolvimento**: Use pastas `tests/`, `debug/` e `logs/`
- **Deploy**: Pastas de desenvolvimento podem ser ignoradas
- **Git**: Configurado para ignorar arquivos temporários

## 🔄 **Manutenção**

1. **Novos testes**: Adicionar em `tests/`
2. **Debug scripts**: Adicionar em `debug/`
3. **Logs**: Documentar em `logs/`
4. **Scripts**: Adicionar em `scripts/`
5. **Raiz**: Manter limpa, apenas essenciais