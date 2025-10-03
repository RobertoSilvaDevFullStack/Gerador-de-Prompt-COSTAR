#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada específico para Railway Deploy
"""

import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar aplicação
from tools.main_demo import app

# Configurar porta da Railway
port = int(os.environ.get("PORT", 8000))

# Exportar app para Railway
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Iniciando aplicação na porta {port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        access_log=True
    )