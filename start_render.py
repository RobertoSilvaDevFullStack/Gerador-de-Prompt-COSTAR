#!/usr/bin/env python3
"""
🚀 Script de inicialização para Render - Otimizado
Evita dependências problemáticas e usa versões simplificadas
"""
import os
import sys
from pathlib import Path

# Configurar Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configurar variáveis de ambiente padrão
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('PIP_NO_CACHE_DIR', '1')

def main():
    """Inicializa servidor para produção no Render com fallbacks"""
    
    print("🚀 Iniciando COSTAR Generator no Render")
    print(f"🐍 Python: {sys.version}")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    
    # Configurar porta
    port = int(os.environ.get("PORT", 8000))
    print(f"📡 Porta: {port}")
    
    # Tentar importar dependências essenciais
    try:
        import uvicorn
        print("✅ Uvicorn disponível")
    except ImportError:
        print("❌ Erro: Uvicorn não encontrado")
        sys.exit(1)
    
    # Importar aplicação com fallback
    app = None
    try:
        from main import app
        print("✅ Aplicação principal (main.py) carregada")
    except Exception as e:
        print(f"⚠️ Erro ao carregar main.py: {e}")
        try:
            from main_demo import app
            print("✅ Fallback para main_demo.py")
        except Exception as e2:
            print(f"❌ Erro ao carregar main_demo.py: {e2}")
            # Criar app básico de emergência
            from fastapi import FastAPI
            app = FastAPI(title="COSTAR Generator - Emergency Mode")
            
            @app.get("/")
            async def emergency_root():
                return {"status": "emergency", "message": "Sistema em modo de emergência"}
            
            @app.get("/api/status/health")
            async def emergency_health():
                return {"status": "ok", "mode": "emergency"}
            
            print("🆘 Aplicação de emergência criada")
    
    # Configurar e iniciar servidor
    try:
        print(f"🔥 Iniciando servidor em 0.0.0.0:{port}")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            workers=1,
            access_log=True,
            log_level="info",
            timeout_keep_alive=5
        )
    except Exception as e:
        print(f"💥 Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()