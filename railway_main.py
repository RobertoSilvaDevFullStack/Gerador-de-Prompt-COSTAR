#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Ponto de entrada específico para Railway Deploy
Gerador de Prompt COSTAR - Versão Otimizada
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging primeiro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger.info(f"🏠 Project root: {project_root}")
logger.info(f"🐍 Python path: {sys.path}")

try:
    logger.info("📦 Importando aplicação...")
    # Importar aplicação
    from tools.main_demo import app
    logger.info("✅ Aplicação importada com sucesso!")
    
    # Configurar porta da Railway
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🔌 Porta configurada: {port}")
    
    # Exportar app para Railway
    __all__ = ['app']
    
except Exception as e:
    logger.error(f"❌ Erro ao importar aplicação: {e}")
    logger.error(f"📍 Diretório atual: {os.getcwd()}")
    logger.error(f"📁 Arquivos disponíveis: {os.listdir('.')}")
    raise

if __name__ == "__main__":
    try:
        import uvicorn
        logger.info(f"🚀 Iniciando aplicação na porta {port}")
        logger.info("🌐 Host: 0.0.0.0")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"💥 Erro ao iniciar servidor: {e}")
        raise