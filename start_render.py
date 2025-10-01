#!/usr/bin/env python3
"""
🚀 Script de inicialização para Render - Ultra otimizado
Prioriza versão minimalista que funciona garantidamente
"""
import os
import sys

def main():
    """Inicializa servidor com máxima compatibilidade"""
    
    print("🚀 Iniciando COSTAR Generator no Render")
    print(f"🐍 Python: {sys.version}")
    
    # Configurar porta
    port = int(os.environ.get("PORT", 8000))
    print(f"📡 Porta: {port}")
    
    # Tentar versão minimalista primeiro (sem dependências problemáticas)
    try:
        print("🎯 Tentando versão minimalista...")
        from app_render import app, main as app_main
        print("✅ Versão minimalista carregada - ZERO dependências Rust")
        app_main()
        return
    except Exception as e:
        print(f"⚠️ Versão minimalista falhou: {e}")
    
    # Fallback para versão principal
    try:
        print("🔄 Fallback para main.py...")
        import uvicorn
        from main import app
        print("✅ Versão principal carregada")
        uvicorn.run(app, host="0.0.0.0", port=port)
        return
    except Exception as e:
        print(f"⚠️ Main.py falhou: {e}")
    
    # Fallback para demo
    try:
        print("🔄 Fallback para main_demo.py...")
        import uvicorn
        from main_demo import app
        print("✅ Versão demo carregada")
        uvicorn.run(app, host="0.0.0.0", port=port)
        return
    except Exception as e:
        print(f"⚠️ Demo falhou: {e}")
    
    # Último recurso - app básico
    try:
        print("🆘 Criando app de emergência...")
        import uvicorn
        from fastapi import FastAPI
        
        emergency_app = FastAPI(title="COSTAR - Emergency Mode")
        
        @emergency_app.get("/")
        async def emergency_home():
            return {"status": "emergency", "message": "Sistema em modo de emergência"}
        
        @emergency_app.get("/api/status/health")
        async def emergency_health():
            return {"status": "ok", "mode": "emergency"}
        
        print("🆘 App de emergência criado")
        uvicorn.run(emergency_app, host="0.0.0.0", port=port)
        
    except Exception as e:
        print(f"💥 Falha total: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()