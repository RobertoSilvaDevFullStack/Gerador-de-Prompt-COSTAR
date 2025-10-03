#!/bin/bash

# Script de inicialização para Railway
echo "🚀 Iniciando deploy na Railway..."
echo "📁 Diretório atual: $(pwd)"
echo "📋 Arquivos disponíveis:"
ls -la

echo "🐍 Executando start.py..."
exec python start.py