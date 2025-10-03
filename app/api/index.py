#!/usr/bin/env python3
"""
🚀 COSTAR Generator - API para Vercel
Sistema completo com FastAPI + Supabase + Multi-IA
"""
import os
import sys
from pathlib import Path

# Configurar Python path para Vercel
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Importar dependências essenciais
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

# Configurar variáveis de ambiente
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

# Criar app FastAPI
app = FastAPI(
    title="COSTAR Generator",
    description="Sistema completo de geração de prompts COSTAR",
    version="3.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tentar importar sistema completo
try:
    # Importar serviços se disponíveis
    sys.path.append(str(current_dir))
    
    # Teste de importação gradual
    supabase_available = False
    multi_ai_available = False
    
    try:
        from app.services.supabase_base_service import SupabaseService
        supabase_available = True
    except:
        pass
    
    try:
        from app.services.multi_ai_service import MultiAIService
        multi_ai_available = True
    except:
        pass
    
    print(f"🔧 Supabase: {supabase_available}")
    print(f"🤖 Multi-IA: {multi_ai_available}")
    
except Exception as e:
    print(f"⚠️ Importação parcial: {e}")

# Página inicial
@app.get("/", response_class=HTMLResponse)
async def home():
    """Página inicial com interface COSTAR"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎯 COSTAR Generator</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .costar-card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="text-center text-white mb-5">
                <h1 class="display-4">🎯 COSTAR Generator</h1>
                <p class="lead">Sistema completo funcionando na Vercel!</p>
            </div>
            
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card costar-card">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="bi bi-magic"></i> Gerador COSTAR</h5>
                        </div>
                        <div class="card-body">
                            <form id="costarForm">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label"><strong>C</strong>ontext</label>
                                        <textarea class="form-control" id="context" rows="3" placeholder="Descreva o contexto..."></textarea>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label"><strong>O</strong>bjective</label>
                                        <textarea class="form-control" id="objective" rows="3" placeholder="Qual o objetivo?"></textarea>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label"><strong>S</strong>tyle</label>
                                        <input type="text" class="form-control" id="style" placeholder="Ex: formal, casual...">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label"><strong>T</strong>one</label>
                                        <input type="text" class="form-control" id="tone" placeholder="Ex: profissional, amigável...">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label"><strong>A</strong>udience</label>
                                        <input type="text" class="form-control" id="audience" placeholder="Para quem é?">
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label"><strong>R</strong>esponse</label>
                                        <input type="text" class="form-control" id="response" placeholder="Formato da resposta">
                                    </div>
                                </div>
                                <div class="mt-4">
                                    <button type="submit" class="btn btn-primary btn-lg">
                                        <i class="bi bi-magic"></i> Gerar Prompt
                                    </button>
                                </div>
                            </form>
                            
                            <div id="result" class="mt-4" style="display: none;">
                                <h5>✨ Prompt Gerado:</h5>
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <pre id="generatedPrompt"></pre>
                                        <button class="btn btn-outline-primary" onclick="copyToClipboard()">
                                            📋 Copiar
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('costarForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = {
                    context: document.getElementById('context').value,
                    objective: document.getElementById('objective').value,
                    style: document.getElementById('style').value,
                    tone: document.getElementById('tone').value,
                    audience: document.getElementById('audience').value,
                    response: document.getElementById('response').value
                };
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    document.getElementById('generatedPrompt').textContent = data.prompt;
                    document.getElementById('result').style.display = 'block';
                } catch (error) {
                    alert('Erro ao gerar prompt: ' + error.message);
                }
            });
            
            function copyToClipboard() {
                const text = document.getElementById('generatedPrompt').textContent;
                navigator.clipboard.writeText(text).then(() => {
                    alert('Prompt copiado!');
                });
            }
        </script>
    </body>
    </html>
    """

# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "service": "costar-generator",
        "platform": "vercel",
        "version": "3.0.0"
    }

@app.get("/api/status")
async def status():
    """Status detalhado do sistema"""
    # Verificar funcionalidades disponíveis
    features = {
        "basic_generation": True,
        "ai_generation": bool(os.getenv("GEMINI_API_KEY")),
        "supabase": bool(os.getenv("SUPABASE_URL")),
        "multi_ai": bool(os.getenv("GROQ_API_KEY"))
    }
    
    return {
        "status": "online",
        "platform": "vercel",
        "features": features,
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.post("/api/generate")
async def generate_prompt(request: Request):
    """Gerar prompt COSTAR"""
    try:
        data = await request.json()
        
        # Estrutura COSTAR básica
        context = data.get("context", "")
        objective = data.get("objective", "")
        style = data.get("style", "")
        tone = data.get("tone", "")
        audience = data.get("audience", "")
        response_format = data.get("response", "")
        
        # Gerar prompt COSTAR
        prompt = f"""CONTEXT: {context}

OBJECTIVE: {objective}

STYLE: {style}

TONE: {tone}

AUDIENCE: {audience}

RESPONSE FORMAT: {response_format}"""
        
        # Tentar usar IA se disponível
        enhanced_prompt = prompt
        ai_used = "basic"
        
        if os.getenv("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                model = genai.GenerativeModel('gemini-pro')
                
                enhancement_request = f"""
                Melhore este prompt COSTAR tornando-o mais específico e eficaz:
                
                {prompt}
                
                Retorne apenas o prompt melhorado, mantendo a estrutura COSTAR.
                """
                
                response = model.generate_content(enhancement_request)
                enhanced_prompt = response.text
                ai_used = "gemini"
            except Exception as e:
                print(f"Erro ao usar Gemini: {e}")
        
        return {
            "status": "success",
            "prompt": enhanced_prompt,
            "ai_used": ai_used,
            "platform": "vercel"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Área de membros
@app.get("/member-area")
async def member_area():
    """Área de membros"""
    return HTMLResponse("<h1>🔐 Área de Membros - Em desenvolvimento</h1>")

# Dashboard admin
@app.get("/admin-dashboard")
async def admin_dashboard():
    """Dashboard administrativo"""
    return HTMLResponse("<h1>🔧 Dashboard Admin - Em desenvolvimento</h1>")

# Para compatibilidade com Vercel
handler = app