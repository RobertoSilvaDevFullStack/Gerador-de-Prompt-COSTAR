#!/bin/bash

# Script de inicialização do COSTAR Prompt Generator Multi-IA
echo "🤖 Iniciando COSTAR Prompt Generator Multi-IA..."

# Verificar se existe arquivo .env
if [ ! -f ../.env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📋 Copiando .env.example para .env..."
    cp ../.env.example ../.env
    echo "⚠️  IMPORTANTE: Configure suas chaves de IA no arquivo .env antes de continuar!"
    echo ""
    echo "🔑 Sistema Multi-IA - Configure pelo menos 2 APIs:"
    echo "- GROQ_API_KEY (Recomendado - Rápido)"
    echo "- GEMINI_API_KEY (Backup principal)"
    echo "- HUGGINGFACE_API_KEY (Opcional)"
    echo "- COHERE_API_KEY (Opcional)"
    echo "- TOGETHER_API_KEY (Opcional)"
    echo ""
    echo "📖 Veja docs/CONFIGURAR_MULTIPLAS_IAS.md para obter as chaves"
    echo ""
    read -p "Pressione Enter após configurar o arquivo .env..."
fi

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose não encontrado. Instale o Docker Compose."
    exit 1
fi

echo "🔧 Parando containers existentes..."
docker-compose -f ../docker/docker-compose.yml down

echo "🏗️  Construindo imagens..."
docker-compose -f ../docker/docker-compose.yml build

echo "🚀 Iniciando serviços..."
docker-compose -f ../docker/docker-compose.yml up -d

echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Verificar se os serviços estão rodando
if docker-compose -f ../docker/docker-compose.yml ps | grep -q "Up"; then
    echo "✅ Serviços Multi-IA iniciados com sucesso!"
    echo ""
    echo "🌐 Aplicação disponível em:"
    echo "   Frontend: http://localhost"
    echo "   API: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
    echo "   Status Multi-IA: http://localhost:8000/api/ai/status"
    echo "   Teste Multi-IA: http://localhost:8000/api/ai/test"
    echo ""
    echo "📊 Para ver logs:"
    echo "   docker-compose -f ../docker/docker-compose.yml logs -f"
    echo ""
    echo "⏹️  Para parar:"
    echo "   docker-compose -f ../docker/docker-compose.yml down"
    echo ""
    echo "🧪 Para testar IAs:"
    echo "   python scripts/test_multi_ai.py"
else
    echo "❌ Erro ao iniciar serviços!"
    echo "📋 Verificando logs..."
    docker-compose -f ../docker/docker-compose.yml logs
fi