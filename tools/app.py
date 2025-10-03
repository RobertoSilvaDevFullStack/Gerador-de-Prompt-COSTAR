#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Prompt COSTAR - Aplicação Principal
Ponto de entrada unificado da aplicação
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Verificar se é execução principal
if __name__ == "__main__":
    # Importar módulo de produção
    try:
        from app.core.application import run_production_app
        run_production_app()
    except ImportError:
        # Fallback para demo se core não estiver disponível
        print("⚠️ Core app não encontrado, executando demo...")
        from main_demo import main as demo_main
        demo_main()
