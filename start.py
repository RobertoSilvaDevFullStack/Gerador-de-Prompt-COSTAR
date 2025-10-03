#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Entrada principal para deploy (Railway/Render/Heroku)
Compatibilidade máxima com diferentes plataformas
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Função principal de entrada"""
    try:
        logger.info("🎯 Iniciando Gerador de Prompt COSTAR")
        
        # Importar aplicação
        from tools.main_demo import app
        logger.info("✅ Aplicação carregada com sucesso")
        
        # Configurar porta
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"🔌 Porta: {port}")
        
        # Iniciar servidor
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()