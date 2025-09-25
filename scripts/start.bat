@echo off
echo 🤖 Iniciando COSTAR Prompt Generator Multi-IA...

REM Verificar se existe arquivo .env
if not exist .env (
    echo ❌ Arquivo .env não encontrado!
    echo 📋 Copiando .env.example para .env...
    copy .env.example .env
    echo ⚠️  IMPORTANTE: Configure suas chaves de IA no arquivo .env antes de continuar!
    echo.
    echo 🔑 Sistema Multi-IA - Configure pelo menos 2 APIs:
    echo - GROQ_API_KEY (Recomendado - Rápido)
    echo - GEMINI_API_KEY (Backup principal)
    echo - HUGGINGFACE_API_KEY (Opcional)
    echo - COHERE_API_KEY (Opcional)
    echo - TOGETHER_API_KEY (Opcional)
    echo.
    echo 📖 Veja docs/CONFIGURAR_MULTIPLAS_IAS.md para obter as chaves
    echo.
    pause
)

REM Verificar se Docker está rodando
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está rodando. Inicie o Docker primeiro.
    pause
    exit /b 1
)

echo 🔧 Parando containers existentes...
cd ..
docker-compose -f docker/docker-compose.yml down

echo 🏗️  Construindo imagens...
docker-compose -f docker/docker-compose.yml build

echo 🚀 Iniciando serviços...
docker-compose -f docker/docker-compose.yml up -d

echo ⏳ Aguardando serviços iniciarem...
timeout /t 10 /nobreak >nul

echo ✅ Serviços Multi-IA iniciados!
echo.
echo 🌐 Aplicação disponível em:
echo    Frontend: http://localhost
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    Status Multi-IA: http://localhost:8000/api/ai/status
echo    Teste Multi-IA: http://localhost:8000/api/ai/test
echo.
echo 📊 Para ver logs: docker-compose -f docker/docker-compose.yml logs -f
echo ⏹️  Para parar: docker-compose -f docker/docker-compose.yml down
echo 🧪 Para testar IAs: python scripts/test_multi_ai.py
echo.
pause