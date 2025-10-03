#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Gerador de Prompt COSTAR - Aplicação Principal
Ponto de entrada unificado e organizado
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Ponto de entrada principal da aplicação"""
    print("🎯 Iniciando Gerador de Prompt COSTAR")
    print("=" * 50)
    
    # Verificar se está em modo desenvolvimento ou produção
    if os.getenv('ENVIRONMENT') == 'production':
        print("🚀 Modo: PRODUÇÃO")
        try:
            # Tentar carregar aplicação otimizada
            from app.core.application import run_production_app
            print("✅ Carregando aplicação otimizada...")
            run_production_app()
        except ImportError:
            print("⚠️ Core app não encontrado, usando demo...")
            import uvicorn
            uvicorn.run("tools.main_demo:app", host="0.0.0.0", port=8000, reload=False)
    else:
        print("🛠️ Modo: DESENVOLVIMENTO")
        try:
            # Carregar versão de desenvolvimento
            import uvicorn
            print("✅ Carregando versão de desenvolvimento...")
            uvicorn.run("tools.main_demo:app", host="0.0.0.0", port=8000, reload=True)
        except ImportError as e:
            print(f"❌ Erro ao carregar aplicação: {e}")
            print("💡 Verifique se todas as dependências estão instaladas")
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)