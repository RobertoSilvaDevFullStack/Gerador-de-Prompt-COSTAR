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

## 📁 Estrutura do Projeto

```
├── 📁 docs/                    # Documentação completa
│   ├── README.md              # Documentação detalhada
│   ├── ANALISE_PROJETO.md     # Análise técnica
│   ├── CONFIGURAR_GEMINI.md   # Setup da API Gemini
│   └── MELHORIAS_IA.md        # Histórico de melhorias
├── 📁 frontend/               # Interface web
│   ├── index.html            # Aplicação principal
│   └── sw.js                 # Service Worker
├── 📁 docker/                 # Containerização
│   ├── docker-compose.yml    # Orquestração
│   ├── Dockerfile.demo       # Imagem da aplicação
│   └── nginx.conf            # Configuração proxy
├── 📁 scripts/               # Scripts de automação
│   ├── start.bat            # Inicialização Windows
│   └── start.sh             # Inicialização Linux/Mac
├── 📁 services/              # Serviços backend
├── 📁 database/              # Migrações DB
├── 📁 backups/               # Backups automáticos
├── main_demo.py              # Aplicação principal
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
