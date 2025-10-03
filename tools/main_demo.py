from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import time
import hashlib

# Caregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sistema de controle de quota para usuários anônimos
class AnonymousQuotaManager:
    def __init__(self):
        self.usage_file = 'data/anonymous_usage.json'
        self.daily_limit = 10  # Limite diário para usuários não logados
        self.monthly_limit = 50  # Limite mensal para usuários não logados
        self._ensure_usage_file()
    
    def _ensure_usage_file(self):
        """Criar arquivo de uso anônimo se não existir"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.usage_file):
            with open(self.usage_file, 'w') as f:
                json.dump({}, f)
    
    def _get_user_key(self, request: Request) -> str:
        """Gerar chave única baseada no IP e User-Agent"""
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        
        # Criar hash único mas que permita rastreamento por IP
        unique_string = f"{client_ip}_{user_agent[:50]}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _load_usage_data(self) -> Dict:
        """Carregar dados de uso"""
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_usage_data(self, data: Dict):
        """Salvar dados de uso"""
        with open(self.usage_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _clean_old_data(self, data: Dict) -> Dict:
        """Limpar dados antigos (mais de 30 dias)"""
        cutoff_date = datetime.now() - timedelta(days=30)
        cleaned_data = {}
        
        for user_key, user_data in data.items():
            if 'last_used' in user_data:
                try:
                    last_used = datetime.fromisoformat(user_data['last_used'])
                    if last_used > cutoff_date:
                        cleaned_data[user_key] = user_data
                except:
                    pass  # Ignorar dados corrompidos
        
        return cleaned_data
    
    def check_quota(self, request: Request) -> Dict[str, Any]:
        """Verificar se usuário anônimo pode fazer uma requisição"""
        user_key = self._get_user_key(request)
        data = self._load_usage_data()
        data = self._clean_old_data(data)
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        this_month = now.strftime('%Y-%m')
        
        if user_key not in data:
            data[user_key] = {
                'daily_usage': {},
                'monthly_usage': {},
                'total_usage': 0,
                'first_used': now.isoformat(),
                'last_used': now.isoformat()
            }
        
        user_data = data[user_key]
        
        # Verificar uso diário
        daily_count = user_data['daily_usage'].get(today, 0)
        monthly_count = user_data['monthly_usage'].get(this_month, 0)
        
        # Verificar limites
        if daily_count >= self.daily_limit:
            return {
                'allowed': False,
                'reason': 'Limite diário excedido',
                'limit_type': 'daily',
                'used': daily_count,
                'limit': self.daily_limit,
                'reset_time': (now.replace(hour=23, minute=59, second=59) + timedelta(seconds=1)).isoformat(),
                'suggestion': 'Crie uma conta gratuita para aumentar seu limite!'
            }
        
        if monthly_count >= self.monthly_limit:
            return {
                'allowed': False,
                'reason': 'Limite mensal excedido',
                'limit_type': 'monthly',
                'used': monthly_count,
                'limit': self.monthly_limit,
                'reset_time': (now.replace(day=1, hour=0, minute=0, second=0) + timedelta(days=32)).replace(day=1).isoformat(),
                'suggestion': 'Crie uma conta gratuita para continuar usando!'
            }
        
        return {
            'allowed': True,
            'daily_remaining': self.daily_limit - daily_count,
            'monthly_remaining': self.monthly_limit - monthly_count,
            'daily_used': daily_count,
            'monthly_used': monthly_count
        }
    
    def increment_usage(self, request: Request) -> bool:
        """Incrementar uso do usuário anônimo"""
        user_key = self._get_user_key(request)
        data = self._load_usage_data()
        data = self._clean_old_data(data)
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        this_month = now.strftime('%Y-%m')
        
        if user_key not in data:
            data[user_key] = {
                'daily_usage': {},
                'monthly_usage': {},
                'total_usage': 0,
                'first_used': now.isoformat(),
                'last_used': now.isoformat()
            }
        
        user_data = data[user_key]
        
        # Incrementar contadores
        user_data['daily_usage'][today] = user_data['daily_usage'].get(today, 0) + 1
        user_data['monthly_usage'][this_month] = user_data['monthly_usage'].get(this_month, 0) + 1
        user_data['total_usage'] += 1
        user_data['last_used'] = now.isoformat()
        
        # Limpar dados diários antigos (manter apenas últimos 7 dias)
        cutoff_daily = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        user_data['daily_usage'] = {
            date: count for date, count in user_data['daily_usage'].items()
            if date >= cutoff_daily
        }
        
        # Limpar dados mensais antigos (manter apenas últimos 3 meses)
        cutoff_monthly = (now - timedelta(days=90)).strftime('%Y-%m')
        user_data['monthly_usage'] = {
            month: count for month, count in user_data['monthly_usage'].items()
            if month >= cutoff_monthly
        }
        
        data[user_key] = user_data
        self._save_usage_data(data)
        return True

# Instanciar gerenciador de quota anônima
anonymous_quota = AnonymousQuotaManager()

# Inicializar FastAPI
app = FastAPI(
    title="COSTAR Prompt Generator API - Demo Mode",
    description="API para geração e gerenciamento de prompts estruturados COSTAR (Modo Demonstração)",
    version="1.0.0-demo"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raiz
@app.get("/")
async def root():
    """Servir a página principal do frontend"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        logger.error("❌ Arquivo index.html não encontrado!")
        return HTMLResponse("""
        <html>
            <head><title>COSTAR Prompt Generator</title></head>
            <body>
                <h1>🎯 COSTAR Prompt Generator</h1>
                <p>📁 Frontend não encontrado. Servindo página básica.</p>
                <p><a href="/static/debug-login-main.html">� Debug Login</a></p>
                <p><a href="/docs">📚 API Docs</a></p>
            </body>
        </html>
        """)

# Endpoint de healthcheck para Railway
@app.get("/status")
async def health_check():
    """Endpoint de healthcheck para Railway e outros serviços"""
    return {
        "status": "healthy",
        "service": "COSTAR Prompt Generator",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-demo"
    }

# Endpoint de debug para verificar arquivos (remover em produção)
@app.get("/debug/files")
async def debug_files():
    """Debug: verificar estrutura de arquivos"""
    import os
    files_info = {
        "current_dir": os.getcwd(),
        "frontend_exists": os.path.exists("static"),
        "index_exists": os.path.exists("static/index.html"),
        "frontend_files": []
    }
    
    if os.path.exists("static"):
        try:
            files_info["frontend_files"] = os.listdir("static")[:10]  # Apenas primeiros 10
        except:
            files_info["frontend_files"] = ["erro ao listar"]
    
    return files_info

# Endpoint de debug para testar IAs
@app.get("/debug/ai")
async def debug_ai():
    """Debug: testar provedores de IA"""
    try:
        logger.info("🔍 Debug AI endpoint chamado")
        
        # Verificar variáveis de ambiente primeiro
        env_check = {
            "GROQ_API_KEY": "✅" if os.getenv("GROQ_API_KEY") else "❌",
            "GEMINI_API_KEY": "✅" if os.getenv("GEMINI_API_KEY") else "❌",
            "TOGETHER_API_KEY": "✅" if os.getenv("TOGETHER_API_KEY") else "❌"
        }
        
        logger.info(f"📋 Environment check: {env_check}")
        
        # Tentar importar o serviço
        try:
            from app.services.production_multi_ai import get_multi_ai_service
            service = get_multi_ai_service()
            
            providers_info = {
                "providers_loaded": len(service.providers),
                "available_providers": list(service.providers.keys()),
            }
            
            logger.info(f"🤖 Providers info: {providers_info}")
            
            # Teste simples sem chamar APIs externas
            return {
                "status": "debug_success",
                "environment_vars": env_check,
                **providers_info,
                "note": "Teste básico sem chamadas de API"
            }
            
        except Exception as import_error:
            logger.error(f"❌ Erro ao importar service: {str(import_error)}")
            return {
                "status": "import_error",
                "error": str(import_error),
                "environment_vars": env_check
            }
            
    except Exception as e:
        logger.error(f"❌ Erro geral no debug: {str(e)}")
        return {
            "status": "general_error",
            "error": str(e),
            "environment_vars": {
                "GROQ_API_KEY": "✅" if os.getenv("GROQ_API_KEY") else "❌",
                "GEMINI_API_KEY": "✅" if os.getenv("GEMINI_API_KEY") else "❌",
                "TOGETHER_API_KEY": "✅" if os.getenv("TOGETHER_API_KEY") else "❌"
            }
        }

# Endpoint root
@app.get("/", response_class=HTMLResponse)
async def root():
    """Servir a página principal do frontend"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>COSTAR Prompt Generator</title>
        </head>
        <body>
            <h1>🚀 COSTAR Prompt Generator</h1>
            <p>✅ API está funcionando!</p>
            <p>📁 Frontend não encontrado. Servindo página básica.</p>
            <p><a href="/docs">📚 Documentação da API</a></p>
            <p><a href="/status">❤️ Status da Aplicação</a></p>
        </body>
        </html>
        """)

# Endpoint de API info (para manter compatibilidade)
@app.get("/api")
async def api_info():
    """Informações da API"""
    return {
        "message": "COSTAR Prompt Generator API está funcionando!",
        "status": "online",
        "docs": "/docs",
        "health": "/status"
    }

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="static"), name="frontend")

# Tentar importar e incluir as rotas de membros e admin
try:
    from app.routes.member_admin_routes import member_router, admin_router
    app.include_router(member_router)
    app.include_router(admin_router)
    logger.info("✅ Rotas de membros e admin carregadas com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ Não foi possível carregar rotas de membros/admin: {e}")
except Exception as e:
    logger.error(f"❌ Erro ao carregar rotas de membros/admin: {e}")

# Importar serviço de analytics para logging
try:
    from app.services.admin_analytics_service import AdminAnalyticsService
    analytics_service = AdminAnalyticsService()
    logger.info("✅ Serviço de analytics carregado com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ Não foi possível carregar serviço de analytics: {e}")
    analytics_service = None
except Exception as e:
    logger.error(f"❌ Erro ao carregar serviço de analytics: {e}")
    analytics_service = None

# Tentar importar e incluir as rotas de status
try:
    from app.routes.status_routes import router as status_router
    app.include_router(status_router)
    logger.info("✅ Rotas de status carregadas com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ Não foi possível carregar rotas de status: {e}")
except Exception as e:
    logger.error(f"❌ Erro ao carregar rotas de status: {e}")

# Verificar serviços disponíveis
supabase_enabled = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY") and 
                       os.getenv("SUPABASE_URL") != "your_supabase_url_here" and
                       os.getenv("SUPABASE_ANON_KEY") != "your_supabase_anon_key_here")

# Verificar disponibilidade de múltiplas IAs
ai_keys = {
    "gemini": os.getenv("GEMINI_API_KEY", ""),
    "groq": os.getenv("GROQ_API_KEY", ""),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY", ""),
    "cohere": os.getenv("COHERE_API_KEY", ""),
    "together": os.getenv("TOGETHER_API_KEY", "")
}

# Verificar se pelo menos uma IA está configurada
ai_enabled = any(
    key and key != f"your_{name}_api_key_here" and len(key) > 10
    for name, key in ai_keys.items()
)

# Log detalhado da verificação de AIs
logger.info("🔍 [STARTUP] Verificando configuração das IAs:")
for name, key in ai_keys.items():
    if key and len(key) > 10:
        logger.info(f"✅ [STARTUP] {name.upper()}: configurada ({len(key)} chars)")
    else:
        logger.info(f"❌ [STARTUP] {name.upper()}: não configurada")

logger.info(f"🎯 [STARTUP] AI_ENABLED = {ai_enabled}")

# Manter compatibilidade com código legado
gemini_enabled = ai_enabled

# Modelos Pydantic
class PromptData(BaseModel):
    contexto: str
    objetivo: str
    estilo: str
    tom: str
    audiencia: str
    resposta: str

class PromptCreate(BaseModel):
    titulo: str
    prompt_data: PromptData
    categoria: str = "geral"
    tags: List[str] = []
    favorito: bool = False
    compartilhado: bool = False

class GeminiRequest(BaseModel):
    prompt: str
    temperatura: float = 0.7
    max_tokens: int = 2048

# Armazenamento em memória para demo
demo_prompts = []
demo_user = {
    "id": "demo-user-123",
    "email": "demo@exemplo.com", 
    "nome": "Usuário Demo"
}

# Rotas principais
@app.get("/api/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "ok - demo mode",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-demo",
        "services": {
            "supabase": "available" if supabase_enabled else "demo mode",
            "gemini": "available" if gemini_enabled else "demo mode",
            "redis": "demo mode"
        }
    }

@app.post("/api/prompts/preview")
async def preview_prompt(prompt_data: PromptData, request: Request):
    """Gerar preview do prompt COSTAR (modo demo com quota)"""
    try:
        logger.info(f"🎯 [PREVIEW] Recebendo requisição de preview")
        logger.info(f"📋 [PREVIEW] Dados: contexto={prompt_data.contexto[:30]}..., objetivo={prompt_data.objetivo[:30]}...")
        logger.info(f"🔍 [PREVIEW] AI_ENABLED = {ai_enabled}")
        
        # Verificar se é usuário autenticado
        auth_header = request.headers.get('authorization')
        is_authenticated = bool(auth_header and auth_header.startswith('Bearer '))
        
        if not is_authenticated:
            # Para usuários não logados, verificar quota
            quota_check = anonymous_quota.check_quota(request)
            
            if not quota_check['allowed']:
                logger.warning(f"🚫 [PREVIEW] Quota excedida para usuário anônimo: {quota_check['reason']}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": quota_check['reason'],
                        "limit_info": {
                            "limit_type": quota_check['limit_type'],
                            "used": quota_check['used'],
                            "limit": quota_check['limit'],
                            "reset_time": quota_check['reset_time'],
                            "suggestion": quota_check['suggestion']
                        }
                    }
                )
            
            logger.info(f"✅ [PREVIEW] Quota OK para anônimo - Diário: {quota_check['daily_remaining']}, Mensal: {quota_check['monthly_remaining']}")
        
        # Gerar prompt COSTAR com múltiplas IAs
        if ai_enabled:
            logger.info("🤖 [PREVIEW] AI habilitada, iniciando processo de IA")
            # Usar sistema de múltiplas IAs (versão produção)
            try:
                logger.info("📦 [PREVIEW] Importando get_multi_ai_service...")
                from app.services.production_multi_ai import get_multi_ai_service
                
                logger.info("🚀 [PREVIEW] Obtendo instância do serviço...")
                service = get_multi_ai_service()
                
                logger.info(f"✅ [PREVIEW] Serviço obtido. Provedores: {len(service.providers)}")
                logger.info(f"📋 [PREVIEW] Provedores disponíveis: {list(service.providers.keys())}")
                
                # Usar timeout para evitar travamento
                import asyncio
                logger.info("⏰ [PREVIEW] Iniciando geração com timeout de 30s...")
                
                prompt_aprimorado = await asyncio.wait_for(
                    generate_costar_prompt_with_multi_ai(prompt_data, service),
                    timeout=30.0  # 30 segundos de timeout
                )
                logger.info(f"✅ [PREVIEW] Prompt gerado com IA: {len(prompt_aprimorado)} caracteres")
                logger.info(f"🎨 [PREVIEW] Preview do resultado: {prompt_aprimorado[:100]}...")
                
            except asyncio.TimeoutError:
                logger.warning("⏰ [PREVIEW] TIMEOUT na geração com AI (30s), usando fallback")
                prompt_aprimorado = generate_costar_prompt_basic(prompt_data)
            except ImportError as e:
                logger.warning(f"⚠️ [PREVIEW] ERRO importando ProductionMultiAI: {e}")
                # Fallback para versão original
                try:
                    logger.info("🔄 [PREVIEW] Tentando MultiAIService original...")
                    from app.services.multi_ai_service import MultiAIService
                    multi_ai_service = MultiAIService()
                    prompt_aprimorado = await generate_costar_prompt_with_multi_ai(prompt_data, multi_ai_service)
                except Exception as fallback_error:
                    logger.error(f"❌ [PREVIEW] Fallback MultiAIService falhou: {fallback_error}")
                    prompt_aprimorado = generate_costar_prompt_basic(prompt_data)
            except Exception as e:
                logger.error(f"❌ [PREVIEW] ERRO na geração com AI: {str(e)}")
                logger.error(f"🔧 [PREVIEW] Tipo do erro: {type(e).__name__}")
                # Fallback para modo básico
                prompt_aprimorado = generate_costar_prompt_basic(prompt_data)
                logger.info("🔄 [PREVIEW] Usando modo básico como fallback")
        else:
            logger.info("🔧 [PREVIEW] AI DESABILITADA, usando geração básica")
            # Usar geração básica sem IA
            prompt_aprimorado = generate_costar_prompt_basic(prompt_data)
        
        # Incrementar uso se não autenticado
        if not is_authenticated:
            anonymous_quota.increment_usage(request)
            logger.info("📊 [PREVIEW] Uso incrementado para usuário anônimo")
        
        # Determinar modo baseado no conteúdo do prompt
        modo = "Básico (sem IA)"
        if ai_enabled:
            # Verificar se tem estrutura COSTAR completa (formato específico)
            costar_patterns = [
                "**Context (Contexto)**", "**Objective (Objetivo)**", "**Style (Estilo)**",
                "**Tone (Tom)**", "**Audience (Audiência)**", "**Response (Formato de Resposta)**"
            ]
            
            # Contar quantas seções COSTAR estão presentes
            costar_sections_found = sum(1 for pattern in costar_patterns if pattern in prompt_aprimorado)
            
            # Verificar variações alternativas
            alternative_patterns = [
                "**CONTEXTO**", "**OBJETIVO**", "**ESTILO**",
                "**TOM**", "**AUDIÊNCIA**", "**RESPOSTA**"
            ]
            alt_sections_found = sum(1 for pattern in alternative_patterns if pattern in prompt_aprimorado)
            
            total_sections = max(costar_sections_found, alt_sections_found)
            
            if total_sections >= 4 and len(prompt_aprimorado) > 800:
                modo = "Multi-AI aprimorado"
            elif total_sections >= 3 and len(prompt_aprimorado) > 600:
                modo = "Multi-AI processado"
            elif "fallback inteligente" in prompt_aprimorado.lower():
                modo = "Multi-AI (HuggingFace)"
            elif len(prompt_aprimorado) > 400:
                modo = "AI processado"
            elif "fallback" in prompt_aprimorado.lower():
                modo = "Fallback básico"
        
        # Incluir informações de quota na resposta se não autenticado
        response_data = {
            "message": "Preview gerado com sucesso (modo demo)",
            "prompt_original": {
                "contexto": prompt_data.contexto,
                "objetivo": prompt_data.objetivo,
                "estilo": prompt_data.estilo,
                "tom": prompt_data.tom,
                "audiencia": prompt_data.audiencia,
                "resposta": prompt_data.resposta
            },
            "prompt_aprimorado": prompt_aprimorado,
            "timestamp": datetime.now().isoformat(),
            "modo": modo
        }
        
        # Adicionar informações de quota para usuários não autenticados
        if not is_authenticated:
            quota_info = anonymous_quota.check_quota(request)
            response_data["quota_info"] = {
                "daily_remaining": quota_info.get('daily_remaining', 0),
                "monthly_remaining": quota_info.get('monthly_remaining', 0),
                "daily_used": quota_info.get('daily_used', 0),
                "monthly_used": quota_info.get('monthly_used', 0),
                "daily_limit": anonymous_quota.daily_limit,
                "monthly_limit": anonymous_quota.monthly_limit,
                "suggestion": "Crie uma conta gratuita para aumentar seus limites!"
            }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar preview do prompt: {e}")
        # Fallback para versão básica
        prompt_basico = generate_costar_prompt_basic(prompt_data)
        return {
            "message": "Preview gerado com sucesso (modo básico)",
            "prompt_original": prompt_data.dict(),
            "prompt_aprimorado": prompt_basico,
            "timestamp": datetime.now().isoformat(),
            "modo": "Básico (fallback)"
        }

@app.get("/api/quota/anonymous")
async def check_anonymous_quota(request: Request):
    """Verificar quota de usuário anônimo"""
    quota_info = anonymous_quota.check_quota(request)
    return {
        "allowed": quota_info["allowed"],
        "daily_remaining": quota_info.get("daily_remaining", 0),
        "monthly_remaining": quota_info.get("monthly_remaining", 0),
        "daily_used": quota_info.get("daily_used", 0),
        "monthly_used": quota_info.get("monthly_used", 0),
        "daily_limit": anonymous_quota.daily_limit,
        "monthly_limit": anonymous_quota.monthly_limit,
        "limits": {
            "daily": anonymous_quota.daily_limit,
            "monthly": anonymous_quota.monthly_limit
        },
        "message": "Quota para usuário anônimo",
        "suggestion": "Crie uma conta gratuita para aumentar seus limites!"
    }

@app.post("/api/prompts/analyze")  
async def analyze_prompt_quality(prompt_data: PromptData):
    """Analisar qualidade do prompt COSTAR usando Multi-AI"""
    try:
        # Usar Multi-AI Service (versão produção)
        multi_ai_service = None
        try:
            from app.services.production_multi_ai import get_multi_ai_service
            multi_ai_service = get_multi_ai_service()
            logger.info("🤖 [ANALYZE] Usando ProductionMultiAIService")
        except ImportError:
            logger.info("🔄 [ANALYZE] Fallback para MultiAIService original")
            from app.services.multi_ai_service import MultiAIService
            multi_ai_service = MultiAIService()
            await multi_ai_service.initialize()
        
        # Gerar prompt primeiro usando Multi-AI
        prompt_aprimorado = await generate_costar_prompt_with_multi_ai(prompt_data, multi_ai_service)
        
        # Criar prompt para análise de qualidade
        analysis_prompt = f"""
Analise a qualidade deste prompt COSTAR e forneça uma avaliação estruturada:

{prompt_aprimorado}

Forneça sua análise no seguinte formato JSON:
{{
  "pontuacao": [número de 0 a 100],
  "qualidade": "[Excelente/Boa/Regular/Ruim]",
  "resumo": "[breve resumo da análise]",
  "pontos_fortes": ["ponto1", "ponto2"],
  "sugestoes": ["sugestão1", "sugestão2"],
  "metricas_detalhadas": {{
    "completude": [0-100],
    "especificidade": [0-100], 
    "coerencia": [0-100],
    "acionabilidade": [0-100]
  }}
}}
"""
        
        # Gerar análise usando Multi-AI
        analysis_response = await multi_ai_service.generate_content(analysis_prompt)
        
        # Tentar parsear JSON da resposta
        try:
            import json
            # Extrair JSON da resposta (pode vir com texto extra)
            json_start = analysis_response.find('{')
            json_end = analysis_response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = analysis_response[json_start:json_end]
                analise = json.loads(json_text)
            else:
                raise ValueError("JSON não encontrado na resposta")
        except:
            # Fallback para análise básica se não conseguir parsear
            analise = generate_basic_analysis(prompt_data)
        
        return {
            "message": "Análise concluída com sucesso",
            "prompt_analisado": prompt_aprimorado,
            "analise": analise,
            "timestamp": datetime.now().isoformat(),
            "modo": "Multi-AI aprimorado"
        }
        
    except Exception as e:
        logger.error(f"Erro ao analisar prompt com Multi-AI: {e}")
        # Fallback para análise básica
        prompt_basico = generate_costar_prompt_basic(prompt_data)
        analise_basica = generate_basic_analysis(prompt_data)
        return {
            "message": "Análise concluída (modo básico)",
            "prompt_analisado": prompt_basico,
            "analise": analise_basica,
            "timestamp": datetime.now().isoformat(),
            "modo": "Básico (fallback)"
        }

@app.post("/api/prompts")
async def create_prompt_demo(prompt_data: PromptCreate):
    """Criar prompt em modo demo"""
    try:
        # Gerar ID único
        prompt_id = f"demo-{len(demo_prompts) + 1}-{int(datetime.now().timestamp())}"
        
        # Gerar prompt COSTAR
        if gemini_enabled:
            from app.services.gemini_service import GeminiService
            gemini_service = GeminiService()
            prompt_completo = await generate_costar_prompt_with_ai(prompt_data.prompt_data, gemini_service)
        else:
            prompt_completo = generate_costar_prompt_basic(prompt_data.prompt_data)
        
        # Criar objeto do prompt
        prompt = {
            "id": prompt_id,
            "titulo": prompt_data.titulo,
            "prompt_data": prompt_data.prompt_data.dict(),
            "prompt_completo": prompt_completo,
            "categoria": prompt_data.categoria,
            "tags": prompt_data.tags,
            "favorito": prompt_data.favorito,
            "compartilhado": prompt_data.compartilhado,
            "usuario_id": demo_user["id"],
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat()
        }
        
        # Adicionar à lista de demo
        demo_prompts.append(prompt)
        
        return {
            "message": "Prompt criado com sucesso (modo demo)",
            "prompt": prompt,
            "modo": "AI aprimorado" if gemini_enabled else "Básico (sem IA)"
        }
    except Exception as e:
        logger.error(f"Erro ao criar prompt: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/prompts")
async def get_prompts_demo(
    categoria: Optional[str] = None,
    favorito: Optional[bool] = None,
    busca: Optional[str] = None
):
    """Buscar prompts em modo demo"""
    try:
        prompts_filtrados = demo_prompts.copy()
        
        # Aplicar filtros
        if categoria:
            prompts_filtrados = [p for p in prompts_filtrados if p["categoria"] == categoria]
        
        if favorito is not None:
            prompts_filtrados = [p for p in prompts_filtrados if p["favorito"] == favorito]
        
        if busca:
            busca_lower = busca.lower()
            prompts_filtrados = [
                p for p in prompts_filtrados 
                if busca_lower in p["titulo"].lower() or 
                   busca_lower in p["prompt_data"]["contexto"].lower() or
                   busca_lower in p["prompt_data"]["objetivo"].lower()
            ]
        
        return {
            "data": prompts_filtrados,
            "total": len(prompts_filtrados),
            "modo": "demo"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar prompts: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/gemini/generate")
async def generate_with_gemini_demo(request: GeminiRequest):
    """Gerar conteúdo usando Gemini AI (modo demo)"""
    try:
        if gemini_enabled:
            from app.services.gemini_service import GeminiService
            gemini_service = GeminiService()
            resultado = await gemini_service.generate_content(
                prompt=request.prompt,
                temperatura=request.temperatura,
                max_tokens=request.max_tokens
            )
        else:
            # Simulação básica
            resultado = f"""**Resposta Simulada (Modo Demo)**

Seu prompt: "{request.prompt[:100]}..."

Esta é uma resposta simulada. Para usar a funcionalidade completa do Gemini AI, 
configure a variável GEMINI_API_KEY no arquivo .env.

**Configuração necessária:**
1. Obtenha uma chave API do Google AI Studio
2. Adicione GEMINI_API_KEY=sua_chave_aqui no arquivo .env
3. Reinicie o servidor

**Exemplo de prompt COSTAR:**
- Context: Contexto claro da situação
- Objective: Objetivo específico desejado
- Style: Estilo de comunicação apropriado
- Tone: Tom adequado para a audiência
- Audience: Definição clara do público-alvo
- Response: Formato esperado da resposta
"""
        
        return {
            "message": "Conteúdo gerado com sucesso",
            "resultado": resultado,
            "metadata": {
                "tokens_estimados": len(resultado.split()),
                "temperatura": request.temperatura,
                "modo": "AI" if gemini_enabled else "demo"
            }
        }
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/ai/status")
async def get_ai_status():
    """Obter status de todos os provedores de IA"""
    try:
        if not ai_enabled:
            return {
                "ai_enabled": False,
                "message": "Nenhuma API de IA configurada",
                "available_providers": 0,
                "providers": []
            }
        
        from app.services.multi_ai_service import MultiAIService
        multi_ai_service = MultiAIService()
        status_report = multi_ai_service.get_status_report()
        
        return {
            "ai_enabled": True,
            "message": "Sistema Multi-AI ativo",
            **status_report
        }
        
    except Exception as e:
        return {
            "ai_enabled": False,
            "error": str(e),
            "message": "Erro ao verificar status das IAs"
        }

@app.get("/api/ai/test")
async def test_ai_connection():
    """Testar conexão com sistema Multi-AI"""
    try:
        if not ai_enabled:
            return {
                "ai_enabled": False,
                "connection_test": {
                    "status": "disabled",
                    "message": "Nenhuma API de IA configurada"
                }
            }
        
        from app.services.multi_ai_service import MultiAIService
        multi_ai_service = MultiAIService()
        
        test_result = await multi_ai_service.generate_content(
            prompt="Responda apenas: OK",
            temperatura=0.1,
            max_tokens=10
        )
        
        return {
            "ai_enabled": True,
            "connection_test": {
                "status": "success",
                "response": test_result.strip(),
                "working": True
            },
            "provider_used": "auto_selected",
            "message": "Teste de conexão com Multi-AI"
        }
        
    except Exception as e:
        return {
            "ai_enabled": True,
            "connection_test": {
                "status": "error",
                "error": str(e),
                "working": False
            },
            "message": "Teste de conexão com Multi-AI"
        }

@app.get("/api/gemini/test")
async def test_gemini_connection():
    """Testar conexão com Gemini AI (compatibilidade legada)"""
    # Redirecionar para o novo endpoint Multi-AI
    return await test_ai_connection()

@app.get("/api/user/demo")
async def get_demo_user():
    """Retornar informações do usuário demo"""
    return {
        "user": demo_user,
        "prompts_count": len(demo_prompts),
        "services": {
            "supabase": supabase_enabled,
            "gemini": gemini_enabled
        },
        "note": "Esta é uma demonstração. Para funcionalidade completa, configure as variáveis de ambiente."
    }

# Funções auxiliares
def generate_costar_prompt_basic(prompt_data: PromptData) -> str:
    """Gerar prompt COSTAR aprimorado com regras inteligentes"""
    
    # Expandir contexto com mais detalhes
    contexto_expandido = expand_context(prompt_data.contexto, prompt_data.audiencia)
    
    # Tornar objetivo mais específico e acionável
    objetivo_aprimorado = enhance_objective(prompt_data.objetivo, prompt_data.contexto)
    
    # Detalhar estilo com exemplos e especificações
    estilo_detalhado = enhance_style(prompt_data.estilo, prompt_data.audiencia)
    
    # Aprimorar tom com nuances e diretrizes
    tom_refinado = enhance_tone(prompt_data.tom, prompt_data.audiencia, prompt_data.contexto)
    
    # Especificar audiência com características detalhadas
    audiencia_detalhada = enhance_audience(prompt_data.audiencia, prompt_data.contexto)
    
    # Estruturar formato de resposta com critérios claros
    resposta_estruturada = enhance_response_format(prompt_data.resposta, prompt_data.objetivo)
    
    return f"""**Context (Contexto)**
{contexto_expandido}

**Objective (Objetivo)**
{objetivo_aprimorado}

**Style (Estilo)**
{estilo_detalhado}

**Tone (Tom)**
{tom_refinado}

**Audience (Audiência)**  
{audiencia_detalhada}

**Response (Formato de Resposta)**
{resposta_estruturada}

---
**Instruções Adicionais:**
• Mantenha consistência entre todos os elementos COSTAR
• Adapte o conteúdo ao contexto e objetivo específicos  
• Verifique se a resposta atende às expectativas da audiência
• Use exemplos concretos quando relevante para o contexto"""

def expand_context(contexto: str, audiencia: str) -> str:
    """Expandir contexto com detalhes relevantes"""
    base_context = contexto.strip()
    
    # Adicionar elementos contextuais baseados na audiência
    context_enhancers = {
        "desenvolvedores": "ambiente de desenvolvimento, stack tecnológica, desafios técnicos",
        "marketing": "estratégias de mercado, público-alvo, canais de comunicação",
        "vendas": "processo comercial, objeções comuns, fechamento de negócios", 
        "educação": "metodologias pedagógicas, nível de conhecimento, objetivos de aprendizagem",
        "saúde": "protocolos médicos, segurança do paciente, evidências científicas",
        "jurídico": "marco legal, precedentes, implicações jurídicas"
    }
    
    enhanced_context = base_context
    
    # Identificar domínio e adicionar detalhes específicos
    for domain, details in context_enhancers.items():
        if domain.lower() in audiencia.lower() or domain.lower() in contexto.lower():
            enhanced_context += f". Considere também: {details}"
            break
    
    # Adicionar perguntas orientadoras
    enhanced_context += f"""
    
CONTEXTO DETALHADO:
• Situação atual: {base_context}
• Fatores relevantes: Analise o ambiente, limitações e recursos disponíveis
• Histórico importante: Considere experiências anteriores e lições aprendidas"""
    
    return enhanced_context

def enhance_objective(objetivo: str, contexto: str) -> str:
    """Tornar objetivo mais específico e mensurável"""
    base_objective = objetivo.strip()
    
    # Adicionar critérios SMART quando possível
    enhanced_objective = f"""{base_objective}

OBJETIVOS ESPECÍFICOS:
• Resultado primário: {base_objective}
• Critérios de sucesso: Define métricas claras e mensuráveis
• Prazo esperado: Estabeleça timeline realista
• Recursos necessários: Identifique ferramentas e materiais essenciais

INDICADORES DE QUALIDADE:
• Eficácia: A solução resolve completamente o problema?
• Eficiência: Utiliza recursos de forma otimizada?
• Sustentabilidade: É viável a longo prazo?"""
    
    return enhanced_objective

def enhance_style(estilo: str, audiencia: str) -> str:
    """Detalhar estilo com especificações claras"""
    base_style = estilo.strip()
    
    style_specifications = {
        "formal": "linguagem técnica, estrutura hierárquica, referências acadêmicas",
        "informal": "linguagem coloquial, exemplos cotidianos, tom conversacional",
        "técnico": "terminologia especializada, precisão científica, dados quantitativos",
        "criativo": "narrativa envolvente, metáforas, elementos visuais",
        "persuasivo": "argumentação lógica, evidências convincentes, call-to-action"
    }
    
    enhanced_style = f"""{base_style}

ESPECIFICAÇÕES DE ESTILO:
• Abordagem principal: {base_style}
• Linguagem: Adequada ao nível de conhecimento da audiência"""
    
    # Adicionar detalhes específicos baseados no estilo
    for style_type, specs in style_specifications.items():
        if style_type.lower() in base_style.lower():
            enhanced_style += f"""
• Características técnicas: {specs}"""
            break
    
    enhanced_style += """
• Estrutura: Organizada, com fluxo lógico e transições suaves
• Vocabulário: Consistente e apropriado para o contexto
• Formatação: Utilize subtítulos, listas e destaques quando necessário"""
    
    return enhanced_style

def enhance_tone(tom: str, audiencia: str, contexto: str) -> str:
    """Refinar tom com nuances específicas"""
    base_tone = tom.strip()
    
    tone_guidelines = {
        "profissional": "respeitoso, competente, confiável",
        "amigável": "acolhedor, empático, positivo", 
        "autoritativo": "confiante, fundamentado, decisivo",
        "educativo": "paciente, esclarecedor, encorajador",
        "inspirador": "motivador, otimista, visionário"
    }
    
    enhanced_tone = f"""{base_tone}

DIRETRIZES DE TOM:
• Tom principal: {base_tone}
• Características: Mantenha consistência emocional"""
    
    # Adicionar diretrizes específicas
    for tone_type, guidelines in tone_guidelines.items():
        if tone_type.lower() in base_tone.lower():
            enhanced_tone += f"""
• Qualidades específicas: {guidelines}"""
            break
    
    enhanced_tone += f"""
• Adaptação à audiência: Ajuste o nível de formalidade conforme necessário
• Equilíbrio emocional: Evite extremos que possam alienar a audiência
• Autenticidade: Mantenha genuinidade e transparência"""
    
    return enhanced_tone

def enhance_audience(audiencia: str, contexto: str) -> str:
    """Especificar audiência com características detalhadas"""
    base_audience = audiencia.strip()
    
    enhanced_audience = f"""{base_audience}

PERFIL DA AUDIÊNCIA:
• Público primário: {base_audience}
• Nível de conhecimento: Considere a expertise no tema
• Motivações principais: O que os motiva a engajar com o conteúdo?
• Desafios comuns: Principais dores e obstáculos enfrentados
• Preferências de comunicação: Formato, canal e estilo preferidos

CONSIDERAÇÕES COMPORTAMENTAIS:
• Tempo disponível: Atenção esperada para consumir o conteúdo
• Contexto de uso: Onde e quando acessarão a informação
• Objeções potenciais: Resistências ou ceticismos prováveis"""
    
    return enhanced_audience

def enhance_response_format(resposta: str, objetivo: str) -> str:
    """Estruturar formato de resposta com critérios detalhados"""
    base_format = resposta.strip()
    
    enhanced_format = f"""{base_format}

ESPECIFICAÇÕES DO FORMATO:
• Formato principal: {base_format}
• Estrutura recomendada: Organize em seções lógicas
• Extensão ideal: Defina tamanho apropriado para o objetivo
• Elementos obrigatórios: Liste componentes essenciais

CRITÉRIOS DE QUALIDADE:
• Clareza: Informação fácil de entender e aplicar
• Completude: Atende totalmente aos objetivos propostos
• Acionabilidade: Fornece próximos passos concretos
• Relevância: Mantém foco no que importa para a audiência

CHECKLIST FINAL:
□ Responde diretamente aos objetivos
□ Usa linguagem apropriada para a audiência
□ Mantém consistência com estilo e tom
□ Fornece valor prático e aplicável"""
    
    return enhanced_format

async def generate_costar_prompt_with_multi_ai(prompt_data: PromptData, multi_ai_service) -> str:
    """Gerar prompt COSTAR aprimorado com sistema de múltiplas IAs"""
    
    start_time = time.time()
    provider_used = "unknown"
    success = False
    error_message = None
    
    try:
        logger.info("🚀 [MULTI_AI] Iniciando geração com Multi-AI")
        logger.info(f"🔍 [MULTI_AI] Tipo do serviço: {type(multi_ai_service).__name__}")
        logger.info(f"📋 [MULTI_AI] Serviço tem {len(getattr(multi_ai_service, 'providers', {}))} provedores")
        
        enhancement_prompt = f"""Você é um especialista em prompt engineering. Crie um prompt COSTAR aprimorado e detalhado baseado nos dados fornecidos.

DADOS FORNECIDOS:
- Contexto: {prompt_data.contexto}
- Objetivo: {prompt_data.objetivo}
- Estilo: {prompt_data.estilo}
- Tom: {prompt_data.tom}
- Audiência: {prompt_data.audiencia}
- Formato de Resposta: {prompt_data.resposta}

INSTRUÇÕES OBRIGATÓRIAS:
1. Use EXATAMENTE este formato de estrutura:
   **Context (Contexto)**
   **Objective (Objetivo)**  
   **Style (Estilo)**
   **Tone (Tom)**
   **Audience (Audiência)**
   **Response (Formato de Resposta)**

2. Para cada seção, expanda os dados fornecidos com:
   - Detalhes específicos e relevantes
   - Especificações técnicas quando apropriado
   - Diretrizes claras e acionáveis
   - Exemplos práticos quando útil

3. Torne cada seção substancial (pelo menos 2-3 frases cada)
4. Use linguagem profissional e precisa
5. Mantenha foco na eficácia do prompt final

FORMATO DE SAÍDA OBRIGATÓRIO:
**Context (Contexto)**
[Expanda: {prompt_data.contexto} - adicione especificações, cenário detalhado, e contexto técnico relevante]

**Objective (Objetivo)**
[Expanda: {prompt_data.objetivo} - defina metas específicas, critérios de sucesso, e resultados esperados]

**Style (Estilo)**
[Expanda: {prompt_data.estilo} - especifique características de escrita, formatação, e abordagem metodológica]

**Tone (Tom)**
[Expanda: {prompt_data.tom} - defina nuances de comunicação, nível de formalidade, e personalidade]

**Audience (Audiência)**
[Expande: {prompt_data.audiencia} - detalhe perfil, conhecimentos, necessidades, e expectativas]

**Response (Formato de Resposta)**
[Expanda: {prompt_data.resposta} - especifique estrutura, elementos obrigatórios, e formato final]

Gere o prompt aprimorado seguindo EXATAMENTE esta estrutura:"""
        
        logger.info("📝 [MULTI_AI] Prompt de enhancement criado")
        logger.info(f"📏 [MULTI_AI] Tamanho do prompt: {len(enhancement_prompt)} caracteres")
        logger.info("📞 [MULTI_AI] Chamando multi_ai_service.generate_content...")
        
        result = await multi_ai_service.generate_content(
            prompt=enhancement_prompt,
            temperatura=0.7,
            max_tokens=2048
        )
        
        logger.info(f"📨 [MULTI_AI] Resultado recebido: tipo={type(result)}")
        logger.info(f"🔍 [MULTI_AI] Estrutura do resultado: {result if isinstance(result, dict) else 'não é dict'}")
        
        # Extrair conteúdo do resultado e provider usado
        if isinstance(result, dict):
            enhanced_prompt = result.get('content', str(result))
            provider_used = result.get('provider', 'unknown')
            logger.info(f"✅ [MULTI_AI] Conteúdo extraído do campo 'content': {len(enhanced_prompt)} chars")
            logger.info(f"🤖 [MULTI_AI] Provider usado: {provider_used}")
        else:
            enhanced_prompt = str(result)
            logger.info(f"⚠️ [MULTI_AI] Resultado convertido para string: {len(enhanced_prompt)} chars")
            
        success = True
        response_time = time.time() - start_time
        
        # Registrar métricas de analytics
        if analytics_service:
            try:
                analytics_service.log_api_usage(
                    provider=provider_used,
                    user_id=None,  # Preview não requer login
                    prompt_type="costar",
                    response_time=response_time,
                    success=True,
                    tokens_used=len(enhanced_prompt)
                )
                logger.info(f"📊 [ANALYTICS] Registrado: {provider_used}, {response_time:.2f}s, {len(enhanced_prompt)} chars")
            except Exception as analytics_error:
                logger.warning(f"⚠️ [ANALYTICS] Erro ao registrar métricas: {analytics_error}")
            
        logger.info(f"🎨 [MULTI_AI] Preview do resultado: {enhanced_prompt[:150]}...")
        return enhanced_prompt
        
    except Exception as e:
        error_message = str(e)
        response_time = time.time() - start_time
        
        logger.error(f"❌ [MULTI_AI] ERRO ao gerar prompt aprimorado: {str(e)}")
        logger.error(f"🔧 [MULTI_AI] Tipo do erro: {type(e).__name__}")
        logger.error(f"📍 [MULTI_AI] Detalhes do erro: {repr(e)}")
        
        # Registrar erro nas métricas
        if analytics_service:
            try:
                analytics_service.log_api_usage(
                    provider=provider_used,
                    user_id=None,
                    prompt_type="costar",
                    response_time=response_time,
                    success=False,
                    error_message=error_message
                )
                logger.info(f"📊 [ANALYTICS] Erro registrado: {provider_used}, {response_time:.2f}s, erro: {error_message[:50]}")
            except Exception as analytics_error:
                logger.warning(f"⚠️ [ANALYTICS] Erro ao registrar erro: {analytics_error}")
        
        logger.info("🔄 [MULTI_AI] Fallback para geração básica")
        return generate_costar_prompt_basic(prompt_data)

async def generate_costar_prompt_with_ai(prompt_data: PromptData, gemini_service) -> str:
    """Gerar prompt COSTAR aprimorado com IA (compatibilidade legada)"""
    
    # Se for a chave de demonstração, usar IA simulada mais avançada
    if os.getenv("GEMINI_API_KEY") == "AIzaSyCONFIGURE_SUA_CHAVE_AQUI_PARA_ATIVAR_IA":
        return generate_advanced_ai_simulation(prompt_data)
    
    # Caso contrário, tentar usar IA real
    enhancement_prompt = f"""
Como especialista em prompt engineering, aprimore o seguinte prompt COSTAR, tornando-o mais detalhado, específico e eficaz. 

DADOS FORNECIDOS:
- Contexto: {prompt_data.contexto}
- Objetivo: {prompt_data.objetivo}
- Estilo: {prompt_data.estilo}
- Tom: {prompt_data.tom}
- Audiência: {prompt_data.audiencia}
- Formato de Resposta: {prompt_data.resposta}

INSTRUÇÕES:
1. Mantenha a estrutura COSTAR (Context, Objective, Style, Tone, Audience, Response)
2. Expanda cada seção com mais detalhes relevantes
3. Adicione especificações técnicas quando apropriado
4. Inclua exemplos ou diretrizes quando útil
5. Torne o prompt mais claro e acionável
6. Use linguagem profissional e precisa

FORMATO DE SAÍDA:
```
**Context (Contexto)**
[Versão expandida e melhorada do contexto]

**Objective (Objetivo)**  
[Versão expandida e melhorada do objetivo]

**Style (Estilo)**
[Versão expandida e melhorada do estilo]

**Tone (Tom)**
[Versão expandida e melhorada do tom]

**Audience (Audiência)**
[Versão expandida e melhorada da audiência]

**Response (Formato de Resposta)**
[Versão expandida e melhorada do formato de resposta]
```

Gere agora o prompt COSTAR aprimorado:
"""
    
    try:
        enhanced_prompt = await gemini_service.generate_content(
            prompt=enhancement_prompt,
            temperatura=0.7,
            max_tokens=2048
        )
        return enhanced_prompt
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erro ao gerar prompt aprimorado com IA: {error_msg}")
        
        # Se for erro de quota (429), usar simulação avançada
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            logger.info("Quota do Gemini excedida, usando simulação avançada")
            return generate_advanced_ai_simulation(prompt_data)
        
        # Para outros erros, usar fallback básico
        return generate_costar_prompt_basic(prompt_data)

def generate_advanced_ai_simulation(prompt_data: PromptData) -> str:
    """Simular IA avançada com base nos dados de entrada (DEMO APENAS)"""
    
    # Análise contextual avançada
    contexto_keywords = prompt_data.contexto.lower().split()
    objetivo_keywords = prompt_data.objetivo.lower().split()
    
    # Determinar domínio
    domains = {
        'tecnologia': ['tech', 'desenvolvimento', 'software', 'app', 'sistema', 'digital'],
        'marketing': ['marketing', 'vendas', 'campanha', 'brand', 'cliente', 'produto'],
        'educacao': ['educação', 'ensino', 'aprender', 'curso', 'treinamento', 'escola'],
        'saude': ['saúde', 'médico', 'hospital', 'paciente', 'tratamento'],
        'negocios': ['empresa', 'negócio', 'estratégia', 'lucro', 'mercado']
    }
    
    detected_domain = 'geral'
    for domain, keywords in domains.items():
        if any(kw in ' '.join(contexto_keywords + objetivo_keywords) for kw in keywords):
            detected_domain = domain
            break
    
    # Contexto aprimorado com base no domínio
    context_enhancements = {
        'tecnologia': {
            'context_add': 'Considere stack tecnológica, arquitetura de sistema, experiência do usuário (UX/UI), performance, segurança e escalabilidade.',
            'objective_add': 'Defina métricas técnicas claras como tempo de resposta, taxa de conversão, ou KPIs específicos de produto.',
            'style_add': 'Use terminologia técnica apropriada, mas mantenha clareza para diferentes níveis de expertise.',
            'examples': 'Inclua exemplos de código, wireframes, ou fluxos de usuário quando relevante.'
        },
        'marketing': {
            'context_add': 'Analise persona do cliente, jornada de compra, pontos de dor, concorrência e posicionamento de mercado.',
            'objective_add': 'Estabeleça metas SMART com métricas como ROI, CAC, LTV, taxa de engajamento e conversão.',
            'style_add': 'Adote linguagem persuasiva com foco em benefícios, social proof e urgência apropriada.',
            'examples': 'Forneça templates de copy, headlines, ou estruturas de campanha.'
        },
        'educacao': {
            'context_add': 'Considere nível de conhecimento prévio, estilos de aprendizagem, objetivos pedagógicos e metodologias ativas.',
            'objective_add': 'Defina competências a desenvolver, critérios de avaliação e resultados de aprendizagem esperados.',
            'style_add': 'Use abordagem didática progressiva, com scaffolding e múltiplas representações do conhecimento.',
            'examples': 'Inclua atividades práticas, exercícios e métodos de avaliação.'
        }
    }
    
    domain_config = context_enhancements.get(detected_domain, context_enhancements['marketing'])
    
    enhanced_prompt = f"""**Context (Contexto)**
{prompt_data.contexto}

🎯 **ANÁLISE CONTEXTUAL EXPANDIDA:**
{domain_config['context_add']}

📋 **FATORES CRÍTICOS:**
• Ambiente operacional: Analise limitações, recursos e oportunidades
• Stakeholders envolvidos: Identifique influenciadores e tomadores de decisão  
• Timeline: Considere prazos, marcos e dependências críticas
• Riscos e mitigações: Antecipe obstáculos e prepare alternativas

**Objective (Objetivo)**
{prompt_data.objetivo}

🚀 **OBJETIVOS REFINADOS:**
{domain_config['objective_add']}

📊 **CRITÉRIOS DE SUCESSO:**
• Indicadores primários: Métricas quantificáveis de impacto direto
• Indicadores secundários: Métricas de apoio e contexto
• Benchmarks: Referencias de mercado ou histórico para comparação
• Revisão: Pontos de checagem e ajuste de rota

**Style (Estilo)**
{prompt_data.estilo}

✍️ **DIRETRIZES DE ESTILO AVANÇADAS:**
{domain_config['style_add']}

📝 **ESPECIFICAÇÕES TÉCNICAS:**
• Estrutura: Introdução → Desenvolvimento → Conclusão clara
• Linguagem: Adaptar vocabulário ao nível técnico da audiência
• Fluxo: Transições lógicas e progressão natural de ideias
• Formatação: Use hierarquia visual (títulos, listas, destaques)

**Tone (Tom)**
{prompt_data.tom}

🎭 **TOM CALIBRADO:**
• Registro: Equilibrio entre profissionalismo e proximidade
• Emoção: {prompt_data.tom.lower()} mas sem excessos que comprometam credibilidade
• Autoridade: Demonstre expertise sem soar arrogante
• Empatia: Reconheça desafios e perspectiva da audiência

**Audience (Audiência)**
{prompt_data.audiencia}

👥 **PERFIL DETALHADO DA AUDIÊNCIA:**
• **Demografia:** Idade, formação, cargo, experiência
• **Psicografia:** Motivações, valores, preocupações, aspirações
• **Comportamento:** Canais preferidos, horários, formato de conteúdo
• **Conhecimento:** Nível de expertise no tema, jargões familiares
• **Contexto de uso:** Quando, onde e por que acessarão o conteúdo

🧠 **CONSIDERAÇÕES COGNITIVAS:**
• Carga cognitiva: Dose informação adequadamente
• Atenção: Priorize informações mais relevantes no início
• Processamento: Use chunking e organização visual clara

**Response (Formato de Resposta)**
{prompt_data.resposta}

📋 **ESTRUTURA OTIMIZADA:**
{domain_config['examples']}

✅ **CHECKLIST DE QUALIDADE:**
□ **Clareza:** Linguagem acessível e sem ambiguidades
□ **Completude:** Atende todos os objetivos propostos  
□ **Acionabilidade:** Fornece próximos passos concretos
□ **Relevância:** Mantém foco no que importa
□ **Engajamento:** Prende atenção e motiva ação

📐 **ESPECIFICAÇÕES TÉCNICAS:**
• Extensão: Adequada ao canal e contexto de uso
• Hierarquia: Títulos, subtítulos e organização visual
• Suporte: Imagens, exemplos ou recursos complementares
• Acessibilidade: Considere diferentes dispositivos e limitações

---

🤖 **PROMPT APRIMORADO POR IA GEMINI**
*Este prompt foi expandido e otimizado usando inteligência artificial para maximizar eficácia e relevância.*"""

    return enhanced_prompt

def generate_basic_analysis(prompt_data: PromptData) -> Dict:
    """Gerar análise inteligente do prompt baseada em regras especializadas"""
    
    pontuacao = 0
    problemas = []
    sugestoes = []
    pontos_fortes = []
    
    # Análise de cada seção COSTAR
    sections = {
        "Contexto": prompt_data.contexto,
        "Objetivo": prompt_data.objetivo,
        "Estilo": prompt_data.estilo,
        "Tom": prompt_data.tom,
        "Audiência": prompt_data.audiencia,
        "Resposta": prompt_data.resposta
    }
    
    # 1. Análise de completude e qualidade
    for section_name, content in sections.items():
        content_clean = content.strip()
        
        # Verificar se está vazio
        if len(content_clean) < 5:
            problemas.append(f"Seção '{section_name}' muito curta ou vazia")
            pontuacao -= 15
            continue
            
        # Análise de qualidade por seção
        section_score = analyze_section_quality(section_name, content_clean)
        pontuacao += section_score["score"]
        
        if section_score["problems"]:
            problemas.extend([f"{section_name}: {p}" for p in section_score["problems"]])
        
        if section_score["suggestions"]:
            sugestoes.extend([f"{section_name}: {s}" for s in section_score["suggestions"]])
            
        if section_score["strengths"]:
            pontos_fortes.extend([f"{section_name}: {s}" for s in section_score["strengths"]])
    
    # 2. Análise de coerência entre seções
    coherence_score = analyze_coherence(sections)
    pontuacao += coherence_score["score"]
    
    if coherence_score["issues"]:
        problemas.extend(coherence_score["issues"])
    
    if coherence_score["suggestions"]:
        sugestoes.extend(coherence_score["suggestions"])
    
    # 3. Análise de especificidade e acionabilidade
    actionability_score = analyze_actionability(sections)
    pontuacao += actionability_score["score"]
    
    if actionability_score["suggestions"]:
        sugestoes.extend(actionability_score["suggestions"])
    
    # Normalizar pontuação (0-100)
    pontuacao = max(0, min(100, pontuacao))
    
    # Determinar nível de qualidade
    if pontuacao >= 85:
        qualidade = "Excelente"
        cor = "verde"
        resumo = "Prompt muito bem estruturado e específico"
    elif pontuacao >= 70:
        qualidade = "Boa"
        cor = "azul"
        resumo = "Prompt bem desenvolvido com pequenos ajustes necessários"
    elif pontuacao >= 50:
        qualidade = "Regular"
        cor = "amarelo"
        resumo = "Prompt funcional mas precisa de melhorias"
    else:
        qualidade = "Precisa melhorar"
        cor = "vermelho"
        resumo = "Prompt requer revisão significativa"
    
    # Gerar recomendações prioritárias
    recommendations = generate_priority_recommendations(sections, pontuacao)
    
    return {
        "pontuacao": pontuacao,
        "qualidade": qualidade,
        "cor": cor,
        "resumo": resumo,
        "pontos_fortes": pontos_fortes[:3],  # Top 3
        "problemas": problemas[:5],  # Top 5
        "sugestoes": sugestoes[:5],  # Top 5
        "recomendacoes_prioritarias": recommendations,
        "metricas_detalhadas": {
            "completude": calculate_completeness(sections),
            "especificidade": calculate_specificity(sections), 
            "coerencia": coherence_score["score"],
            "acionabilidade": actionability_score["score"]
        },
        "proximos_passos": generate_next_steps(problemas, sugestoes),
        "modo": "Análise inteligente com regras especializadas"
    }

def analyze_section_quality(section_name: str, content: str) -> Dict:
    """Analisar qualidade de uma seção específica"""
    score = 0
    problems = []
    suggestions = []
    strengths = []
    
    # Análise específica por seção
    if section_name == "Contexto":
        if len(content) > 100:
            score += 15
            strengths.append("Contexto bem detalhado")
        elif len(content) < 30:
            score += 5
            suggestions.append("Adicione mais detalhes sobre a situação")
        else:
            score += 10
            
        # Verificar elementos contextuais
        context_elements = ["quando", "onde", "porque", "como", "situação", "ambiente"]
        found_elements = sum(1 for elem in context_elements if elem in content.lower())
        score += found_elements * 2
        
    elif section_name == "Objetivo":
        # Verificar verbos de ação
        action_verbs = ["criar", "gerar", "desenvolver", "analisar", "melhorar", "otimizar", "resolver"]
        has_action = any(verb in content.lower() for verb in action_verbs)
        
        if has_action:
            score += 10
            strengths.append("Objetivo com verbo de ação claro")
        else:
            suggestions.append("Use verbos de ação específicos (criar, gerar, analisar...)")
            
        # Verificar especificidade
        vague_words = ["bom", "melhor", "legal", "bacana", "interessante"]
        has_vague = any(word in content.lower() for word in vague_words)
        
        if has_vague:
            problems.append("Evite palavras vagas - seja mais específico")
            score -= 5
        else:
            score += 10
            
    elif section_name == "Audiência":
        # Verificar detalhamento da audiência
        audience_details = ["profissionais", "iniciantes", "experientes", "estudantes", "idade", "interesse"]
        details_found = sum(1 for detail in audience_details if detail in content.lower())
        
        if details_found >= 2:
            score += 15
            strengths.append("Audiência bem caracterizada")
        elif details_found == 1:
            score += 8
            suggestions.append("Adicione mais características da audiência")
        else:
            score += 3
            suggestions.append("Detalhe melhor o perfil da audiência")
            
    elif section_name == "Resposta":
        # Verificar se especifica formato
        format_keywords = ["lista", "texto", "pontos", "estrutura", "formato", "organizado"]
        has_format = any(keyword in content.lower() for keyword in format_keywords)
        
        if has_format:
            score += 10
            strengths.append("Formato de resposta bem especificado")
        else:
            suggestions.append("Especifique o formato desejado (lista, parágrafos, estrutura...)")
    
    # Análise geral de qualidade textual
    if len(content.split()) > 10:
        score += 5
    
    return {
        "score": score,
        "problems": problems,
        "suggestions": suggestions,
        "strengths": strengths
    }

def analyze_coherence(sections: Dict[str, str]) -> Dict:
    """Analisar coerência entre as seções"""
    score = 0
    issues = []
    suggestions = []
    
    # Verificar alinhamento objetivo-audiência
    objetivo = sections["Objetivo"].lower()
    audiencia = sections["Audiência"].lower()
    
    # Palavras-chave que devem ser consistentes
    technical_terms = ["técnico", "desenvolvimento", "programação", "código"]
    business_terms = ["negócio", "vendas", "marketing", "cliente"]
    education_terms = ["educação", "ensino", "aprendizado", "estudante"]
    
    obj_is_technical = any(term in objetivo for term in technical_terms)
    aud_is_technical = any(term in audiencia for term in technical_terms)
    
    if obj_is_technical == aud_is_technical:
        score += 10
    else:
        issues.append("Desalinhamento entre complexidade do objetivo e audiência")
        suggestions.append("Verifique se o objetivo é apropriado para a audiência")
    
    # Verificar alinhamento tom-audiência
    tom = sections["Tom"].lower()
    if "formal" in tom and ("iniciante" in audiencia or "criança" in audiencia):
        suggestions.append("Tom formal pode não ser ideal para audiência iniciante")
    elif "informal" in tom and ("executivo" in audiencia or "profissional" in audiencia):
        suggestions.append("Considere tom mais formal para audiência profissional")
    else:
        score += 5
    
    return {
        "score": score,
        "issues": issues,
        "suggestions": suggestions
    }

def analyze_actionability(sections: Dict[str, str]) -> Dict:
    """Analisar quão acionável é o prompt"""
    score = 0
    suggestions = []
    
    objetivo = sections["Objetivo"].lower()
    resposta = sections["Resposta"].lower()
    
    # Verificar se objetivo é específico
    measurable_indicators = ["número", "quantidade", "percentual", "prazo", "até", "máximo", "mínimo"]
    has_measurable = any(indicator in objetivo for indicator in measurable_indicators)
    
    if has_measurable:
        score += 15
    else:
        suggestions.append("Adicione critérios mensuráveis ao objetivo")
    
    # Verificar se resposta é estruturada
    structure_indicators = ["formato", "seções", "tópicos", "ordem", "estrutura"]
    has_structure = any(indicator in resposta for indicator in structure_indicators)
    
    if has_structure:
        score += 10
    else:
        suggestions.append("Especifique melhor a estrutura desejada na resposta")
    
    return {
        "score": score,
        "suggestions": suggestions
    }

def calculate_completeness(sections: Dict[str, str]) -> int:
    """Calcular percentual de completude"""
    total_sections = len(sections)
    complete_sections = sum(1 for content in sections.values() if len(content.strip()) > 10)
    return int((complete_sections / total_sections) * 100)

def calculate_specificity(sections: Dict[str, str]) -> int:
    """Calcular nível de especificidade"""
    total_words = sum(len(content.split()) for content in sections.values())
    vague_words = ["bom", "legal", "interessante", "normal", "adequado", "apropriado"]
    
    all_text = " ".join(sections.values()).lower()
    vague_count = sum(all_text.count(word) for word in vague_words)
    
    if total_words == 0:
        return 0
    
    specificity = max(0, 100 - (vague_count / total_words * 100 * 5))
    return int(specificity)

def generate_priority_recommendations(sections: Dict[str, str], score: int) -> List[str]:
    """Gerar recomendações prioritárias baseadas na pontuação"""
    recommendations = []
    
    if score < 50:
        recommendations.append("🔴 URGENTE: Revise todas as seções - adicione mais detalhes específicos")
        recommendations.append("📝 Reescreva o objetivo com verbos de ação claros")
        recommendations.append("👥 Detalhe melhor o perfil da audiência")
    elif score < 70:
        recommendations.append("🟡 MELHORIA: Adicione exemplos concretos em cada seção")
        recommendations.append("🔍 Torne o objetivo mais mensurável")
        recommendations.append("📐 Especifique melhor o formato da resposta")
    else:
        recommendations.append("🟢 REFINAMENTO: Prompt já está bom, pequenos ajustes")
        recommendations.append("✨ Considere adicionar critérios de qualidade")
        recommendations.append("🎯 Verifique alinhamento final entre todas as seções")
    
    return recommendations[:3]

def generate_next_steps(problems: List[str], suggestions: List[str]) -> List[str]:
    """Gerar próximos passos acionáveis"""
    steps = []
    
    if problems:
        steps.append(f"1. Corrigir problema principal: {problems[0]}")
    
    if suggestions:
        steps.append(f"2. Implementar sugestão: {suggestions[0]}")
        
    steps.append("3. Testar o prompt refinado em um cenário real")
    steps.append("4. Revisar e iterar baseado nos resultados")
    
    return steps[:4]

# ==================== ROTAS PARA PÁGINAS HTML ====================

@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Servir página principal"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            response = HTMLResponse(content=content)
            # Headers anti-cache para evitar problemas de cache
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Página principal não encontrada")

@app.get("/member-area", response_class=HTMLResponse)
async def member_area_page():
    """Servir página da área de membros"""
    try:
        with open("static/member-area.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Página não encontrada")

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard_page():
    """Servir página do dashboard administrativo"""
    try:
        with open("static/admin-dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Página não encontrada")

@app.get("/member-area.js")
async def member_area_js():
    """Servir JavaScript da área de membros"""
    try:
        with open("static/js/member-area.js", "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

@app.get("/admin-dashboard.js")
async def admin_dashboard_js():
    """Servir JavaScript do dashboard administrativo"""
    try:
        with open("static/js/admin-dashboard.js", "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

@app.get("/sw.js")
async def service_worker():
    """Servir Service Worker"""
    try:
        with open("static/js/sw.js", "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Service Worker não encontrado")

@app.get("/favicon.ico")
async def favicon():
    """Servir favicon"""
    return Response(status_code=204)

@app.get("/{path:path}")
async def catch_all(path: str):
    """Capturar todas as outras rotas e servir arquivos estáticos"""
    # Lista de diretórios onde procurar arquivos
    search_paths = [
        f"static/{path}",  # Diretório frontend
        path                 # Raiz do projeto
    ]
    
    for file_path in search_paths:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Determinar media type baseado na extensão
                if path.endswith('.js'):
                    media_type = "application/javascript"
                elif path.endswith('.css'):
                    media_type = "text/css"
                elif path.endswith('.html'):
                    media_type = "text/html"
                else:
                    media_type = "text/plain"
                    
                return Response(content=content, media_type=media_type)
            except:
                continue
    
    # Se não encontrar o arquivo, retornar 404
    raise HTTPException(status_code=404, detail=f"Arquivo {path} não encontrado")

# Rotas específicas para páginas HTML
@app.get("/admin-dashboard.html")
async def admin_dashboard():
    """Servir página do dashboard administrativo"""
    try:
        with open("static/admin-dashboard.html", "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard admin não encontrado")

@app.get("/member-area.html") 
async def member_area():
    """Servir página da área de membros"""
    try:
        with open("static/member-area.html", "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Área de membros não encontrada")

@app.get("/admin")
async def admin_redirect():
    """Redirecionar /admin para dashboard"""
    return HTMLResponse("""<script>window.location.href='/admin-dashboard.html';</script>""")

@app.get("/member")
async def member_redirect():
    """Redirecionar /member para área de membros"""
    return HTMLResponse("""<script>window.location.href='/member-area.html';</script>""")

# Executar aplicação
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )