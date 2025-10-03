# -*- coding: utf-8 -*-
"""
Gerador de Prompt COSTAR - Core da Aplicação
Módulo principal unificado da aplicação
"""

import uvicorn
import os
from pathlib import Path
import sys

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def run_production_app():
    """Executar aplicação em modo produção"""
    try:
        # Importar aplicação FastAPI do tools/main_demo
        from tools.main_demo import app
        
        # Obter porta da variável de ambiente (padrão 8000)
        port = int(os.getenv("PORT", 8000))
        
        print("🚀 Iniciando Gerador de Prompt COSTAR...")
        print(f"📍 Servidor disponível em: http://localhost:{port}")
        print(f"👥 Admin Dashboard: http://localhost:{port}/admin-dashboard.html")
        print(f"🔐 Área de Membros: http://localhost:{port}/member-area.html")
        
        # Executar servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        sys.exit(1)

def run_development_app():
    """Executar aplicação em modo desenvolvimento"""
    try:
        from tools.main_demo import app
        
        print("🔧 Iniciando em modo DESENVOLVIMENTO...")
        print("📍 Servidor disponível em: http://localhost:8000")
        print("🔄 Hot reload ativado")
        
        uvicorn.run(
            "tools.main_demo:app",
            host="0.0.0.0", 
            port=8000,
            reload=True,
            log_level="debug"
        )
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação em modo dev: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        run_development_app()
    else:
        run_production_app()