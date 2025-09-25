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
│   ├── multi_ai_service.py   # Sistema Multi-IA
│   ├── gemini_service.py     # Serviço Gemini
│   └── outros serviços...    # Cache, backup, etc.
├── 📁 database/              # Migrações DB
├── 📁 backups/               # Backups automáticos
├── main_demo.py              # Aplicação principal
└── requirements.txt          # Dependências Python
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
