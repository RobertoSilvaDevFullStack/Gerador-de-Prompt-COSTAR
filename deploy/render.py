#!/usr/bin/env python3
"""
Launcher para deployment no Render
"""
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from deploy.apps.start_render import main
    main()
