# 🏗️ ARQUITETURA DO SISTEMA SUPABASE

## 📐 VISÃO GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (FastAPI + HTML)                │
├─────────────────────────────────────────────────────────────┤
│                     API ENDPOINTS                           │
│  /api/status/*  │  /api/admin/*  │  /api/members/*         │
├─────────────────────────────────────────────────────────────┤
│                  CAMADA DE SERVIÇOS                         │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ IntegratedData  │    │   Multi-AI      │                │
│  │    Service      │    │    Service      │                │
│  │                 │    │                 │                │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                │
│  │ │ Demo Mode   │ │    │ │ Groq        │ │                │
│  │ │ (Memory)    │ │    │ │ Gemini      │ │                │
│  │ └─────────────┘ │    │ │ HuggingFace │ │                │
│  │       │         │    │ │ Cohere      │ │                │
│  │       ▼         │    │ │ Together    │ │                │
│  │ ┌─────────────┐ │    │ └─────────────┘ │                │
│  │ │ Supabase    │ │    └─────────────────┘                │
│  │ │ Service     │ │                                        │
│  │ └─────────────┘ │                                        │
│  └─────────────────┘                                        │
├─────────────────────────────────────────────────────────────┤
│                    CAMADA DE DADOS                          │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   DEMO DATA     │    │   SUPABASE      │                │
│  │   (In-Memory)   │    │   PostgreSQL    │                │
│  │                 │    │                 │                │
│  │ • prompts: []   │    │ • user_profiles │                │
│  │ • templates: [] │    │ • prompts       │                │
│  │ • ai_logs: []   │    │ • templates     │                │
│  │ • users: {}     │    │ • ratings       │                │
│  └─────────────────┘    │ • ai_usage_logs │                │
│                         │ • settings      │                │
│                         └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 FLUXO DE DECISÃO DE DADOS

```python
def save_prompt(user_id, data):
    if mode == "supabase" and supabase_available:
        return _save_prompt_supabase(user_id, data)
    else:
        return _save_prompt_demo(user_id, data)
```

## 📊 ESTRUTURA DE COMPONENTES

### 1. `integrated_data_service.py` - Orquestrador Principal

```
DataService
├── _initialize_supabase()     # Detecta e inicializa Supabase
├── test_connection()          # Testa conectividade
├── save_prompt()              # Roteamento inteligente
├── get_user_prompts()         # Busca com fallback
├── _save_prompt_supabase()    # Implementação Supabase
└── _save_prompt_demo()        # Implementação Demo
```

### 2. `supabase_base_service.py` - Conexão com Supabase

```
SupabaseService
├── __init__()                 # Inicializa clientes
├── test_connection()          # Testa conectividade
├── get_client()               # Cliente público/admin
├── table_operation()          # CRUD genérico
└── execute_query()            # SQL customizado
```

### 3. `supabase_config.py` - Gerenciamento de Configuração

```
SupabaseConfig
├── is_configured()            # Valida configuração básica
├── has_admin_access()         # Verifica acesso admin
├── get_public_config()        # Config cliente público
├── get_admin_config()         # Config cliente admin
└── validate_environment()     # Validação completa
```

## 🔀 ESTADOS DO SISTEMA

### Estado 1: DEMO MODE (Padrão)

- **Condição:** Supabase não configurado ou falha na conexão
- **Armazenamento:** Memória (session)
- **Persistência:** Não persiste entre reinicializações
- **Vantagens:** Zero configuração, funciona imediatamente
- **Uso:** Demonstração, desenvolvimento inicial

### Estado 2: SUPABASE MODE (Produção)

- **Condição:** Supabase configurado e conectado
- **Armazenamento:** PostgreSQL (Supabase)
- **Persistência:** Dados persistem permanentemente
- **Vantagens:** Produção, escalabilidade, backup
- **Uso:** Sistema em produção

## 🛡️ CAMADAS DE SEGURANÇA

### 1. Validação de Configuração

```python
config_check = check_configuration()
if not config_check['ready_for_public']:
    # Fallback para demo mode
```

### 2. Row Level Security (RLS)

```sql
-- Aplicado automaticamente em todas as tabelas
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see own prompts" ON prompts
FOR SELECT USING (auth.uid() = user_id);
```

### 3. Separação de Clientes

- **Cliente Público:** Com RLS, para operações de usuário
- **Cliente Admin:** Sem RLS, para operações administrativas

## 🔍 SISTEMA DE DIAGNÓSTICO

### Endpoint: `/api/status/health`

```json
{
  "status": "healthy",
  "backend": {
    "mode": "demo|supabase",
    "connected": true,
    "status": "demo_mode_active|connected|error"
  },
  "supabase_config": {
    "configured": true,
    "admin_access": true,
    "validation": {...}
  }
}
```

### Scripts de Diagnóstico:

1. `test_supabase_setup.py` - Teste completo
2. `deploy_supabase_schema.py` - Deploy automático
3. `test_endpoints.py` - Teste de API

## 🚀 ESTRATÉGIA DE MIGRAÇÃO

### Fase 1: Demo Mode (Atual)

```python
# Força demo mode
def _initialize_supabase(self):
    print("ℹ️  Usando modo demo")
    return  # Early return força demo
```

### Fase 2: Configuração Supabase

1. Criar projeto Supabase
2. Configurar `.env` com credenciais
3. Aplicar schema: `python scripts/deploy_supabase_schema.py`

### Fase 3: Ativação Supabase

```python
# Remove early return para ativar Supabase
def _initialize_supabase(self):
    # REMOVER esta linha:
    # return

    if not SUPABASE_AVAILABLE:
        print("ℹ️  Supabase não disponível")
        return
    # ... resto do código
```

## 📈 MONITORAMENTO E MÉTRICAS

### Métricas Coletadas:

- **AI Usage:** Provider, tokens, custo por usuário
- **Prompt Creation:** Frequência, categorias, usuários ativos
- **Template Usage:** Templates mais utilizados, ratings
- **System Health:** Conexões, erros, performance

### Dashboards Disponíveis:

- **Admin Dashboard:** Visão geral do sistema
- **Member Area:** Estatísticas pessoais do usuário
- **Status Endpoints:** Monitoramento técnico em tempo real

## 🎯 BENEFÍCIOS DA ARQUITETURA

1. **Zero Downtime:** Sistema funciona com ou sem Supabase
2. **Migração Gradual:** Demo → Supabase sem quebrar funcionalidades
3. **Fallback Automático:** Se Supabase falha, volta para demo
4. **Testabilidade:** Cada componente pode ser testado independentemente
5. **Escalabilidade:** Arquitetura preparada para crescimento
6. **Manutenibilidade:** Código organizado e documentado

Esta arquitetura garante que o sistema seja robusto, escalável e fácil de manter!
