# Ponto de entrada principal para deployment no Vercel
from main_demo import app

# O Vercel procura por um objeto chamado 'app' em main.py
# Importamos a aplicação FastAPI do main_demo.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)