# Ponto de entrada principal para deployment
import os
from main_demo import app

# Configurar porta para Render (usa variável de ambiente PORT)
port = int(os.environ.get("PORT", 8000))

# O Render e outros serviços procuram por um objeto chamado 'app' em main.py
# Importamos a aplicação FastAPI do main_demo.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)