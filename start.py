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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Função principal de entrada"""
    try:
        logger.info("🎯 INICIANDO GERADOR DE PROMPT COSTAR")
        logger.info(f"📁 Diretório: {project_root}")
        logger.info(f"🐍 Python: {sys.version}")
        
        # Verificar estrutura
        tools_dir = project_root / "tools"
        main_demo = tools_dir / "main_demo.py"
        
        if not tools_dir.exists():
            logger.error("❌ Diretório 'tools' não encontrado!")
            sys.exit(1)
            
        if not main_demo.exists():
            logger.error("❌ Arquivo 'tools/main_demo.py' não encontrado!")
            sys.exit(1)
            
        logger.info("✅ Estrutura do projeto verificada")
        
        # Importar aplicação
        logger.info("📦 Carregando aplicação...")
        from tools.main_demo import app
        logger.info("✅ Aplicação carregada com sucesso")
        
        # Configurar porta
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"🔌 Porta configurada: {port}")
        
        # Verificar variáveis críticas
        logger.info("🔍 Verificando configuração...")
        supabase_url = os.environ.get("SUPABASE_URL", "not_set")
        logger.info(f"📊 Supabase URL: {'configurado' if supabase_url != 'not_set' else 'não configurado'}")
        
        # Iniciar servidor
        logger.info("🚀 Iniciando servidor...")
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {e}")
        logger.error("💡 Verifique se todas as dependências estão instaladas")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        logger.error(f"🔧 Tipo: {type(e).__name__}")
        sys.exit(1)

if __name__ == "__main__":
    main()