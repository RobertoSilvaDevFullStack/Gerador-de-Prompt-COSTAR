@echo off
echo 🚀 Iniciando COSTAR Prompt Generator...

REM Verificar se existe arquivo .env
if not exist .env (
    echo ❌ Arquivo .env não encontrado!
    echo 📋 Copiando .env.example para .env...
    copy .env.example .env
    echo ⚠️  IMPORTANTE: Configure suas chaves no arquivo .env antes de continuar!
    echo.
    echo Você precisa configurar:
    echo - SUPABASE_URL
    echo - SUPABASE_ANON_KEY
    echo - GEMINI_API_KEY
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

echo ✅ Serviços iniciados!
echo.
echo 🌐 Aplicação disponível em:
echo    Frontend: http://localhost
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.
echo 📊 Para ver logs: docker-compose -f docker/docker-compose.yml logs -f
echo ⏹️  Para parar: docker-compose -f docker/docker-compose.yml down
echo.
pause