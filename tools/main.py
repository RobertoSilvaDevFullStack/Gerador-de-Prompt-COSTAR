# Ponto de entrada principal para deployment
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar a aplicação FastAPI do main_demo.py
from tools.main_demo import app

# Configurar porta para Railway/Render (usa variável de ambiente PORT)
port = int(os.environ.get("PORT", 8000))

# O Railway e outros serviços procuram por um objeto chamado 'app' em main.py
# Exportar o app para compatibilidade
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)