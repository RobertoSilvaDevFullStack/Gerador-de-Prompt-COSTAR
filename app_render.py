#!/usr/bin/env python3
"""
🚀 Aplicação minimalista para Render - Zero dependências Rust
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

# Configurar variáveis de ambiente
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

# Criar app FastAPI
app = FastAPI(
    title="COSTAR Generator - Render Edition",
    description="Sistema de geração de prompts COSTAR otimizado para Render",
    version="3.0.0-render"
)

# Servir arquivos estáticos (HTML, CSS, JS)
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except:
    pass  # Continua sem arquivos estáticos se não existir

# Página inicial
@app.get("/", response_class=HTMLResponse)
async def home():
    """Página inicial"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>COSTAR Generator - Render</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-4">🎯 COSTAR Generator</h1>
                    <p class="lead">Sistema de Geração de Prompts</p>
                    <div class="alert alert-success">
                        ✅ Sistema funcionando no Render!
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5>🎯 COSTAR</h5>
                                    <p>Metodologia estruturada para criação de prompts eficazes</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5>🤖 Multi-IA</h5>
                                    <p>Integração com múltiplos provedores de IA</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body">
                                    <h5>☁️ Cloud</h5>
                                    <p>Deploy na nuvem com alta disponibilidade</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

# Health check para Render
@app.get("/api/status/health")
async def health_check():
    """Health check para monitoramento do Render"""
    return {
        "status": "healthy",
        "service": "costar-generator",
        "version": "3.0.0-render",
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "python_version": os.sys.version,
        "deployed_on": "render"
    }

# Status básico
@app.get("/api/status")
async def status():
    """Status do sistema"""
    return {
        "status": "online",
        "message": "COSTAR Generator funcionando no Render",
        "features": {
            "basic_mode": True,
            "render_optimized": True,
            "zero_rust_deps": True
        }
    }

# Endpoint de teste
@app.get("/api/test")
async def test():
    """Endpoint de teste"""
    return {
        "message": "API funcionando!",
        "timestamp": "2025-09-30",
        "platform": "render",
        "status": "success"
    }

# Geração básica de prompts (sem IA por enquanto)
@app.post("/api/generate")
async def generate_prompt(prompt_data: dict):
    """Geração básica de prompts COSTAR"""
    try:
        # Estrutura COSTAR básica
        context = prompt_data.get("context", "")
        objective = prompt_data.get("objective", "")
        style = prompt_data.get("style", "")
        tone = prompt_data.get("tone", "")
        audience = prompt_data.get("audience", "")
        response_format = prompt_data.get("response", "")
        
        # Montar prompt COSTAR
        costar_prompt = f"""
**CONTEXT:** {context}

**OBJECTIVE:** {objective}

**STYLE:** {style}

**TONE:** {tone}

**AUDIENCE:** {audience}

**RESPONSE FORMAT:** {response_format}
"""
        
        return {
            "status": "success",
            "prompt": costar_prompt.strip(),
            "method": "costar_basic",
            "platform": "render"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar prompt: {str(e)}")

# Rotas para páginas específicas
@app.get("/member-area")
async def member_area():
    """Área de membros"""
    try:
        with open("frontend/member-area.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>Área de Membros - Em desenvolvimento</h1>")

@app.get("/admin-dashboard")
async def admin_dashboard():
    """Dashboard admin"""
    try:
        with open("frontend/admin-dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>Dashboard Admin - Em desenvolvimento</h1>")

def main():
    """Função principal para inicialização"""
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 COSTAR Generator - Render Edition")
    print(f"📡 Porta: {port}")
    print("✅ Versão minimalista sem dependências Rust")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()