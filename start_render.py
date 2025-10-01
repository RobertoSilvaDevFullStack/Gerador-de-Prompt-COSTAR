#!/usr/bin/env python3
"""
🚀 Script de inicialização para Render
Configura o ambiente e inicia o servidor FastAPI otimizado para produção
"""
import os
import sys
from pathlib import Path

# Configurar Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configurar variáveis de ambiente padrão se não existirem
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

def main():
    """Inicializa servidor para produção no Render"""
    
    # Log de inicialização
    print("🚀 Iniciando COSTAR Generator no Render")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    print(f"🔧 Debug: {os.environ.get('DEBUG', 'false')}")
    
    # Configurar porta (Render usa variável PORT)
    port = int(os.environ.get("PORT", 8000))
    print(f"📡 Servidor iniciando em 0.0.0.0:{port}")
    
    # Importar aplicação (usando main.py ao invés de main_demo.py para produção)
    try:
        from main import app
        print("✅ Aplicação principal (main.py) carregada com sucesso")
    except ImportError:
        print("⚠️ Fallback para main_demo.py")
        from main_demo import app
    
    # Configuração para produção no Render
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=1,  # Render Free tier tem limitação de CPU/memória
        access_log=True,
        log_level="info",
        loop="asyncio",
        http="httptools"
    )

if __name__ == "__main__":
    main()