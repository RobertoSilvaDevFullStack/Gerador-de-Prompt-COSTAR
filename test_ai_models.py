#!/usr/bin/env python3
"""
Script para testar os modelos AI corrigidos
"""
import asyncio
import os
from dotenv import load_dotenv
from services.production_multi_ai import ProductionMultiAIService

# Carrega variáveis de ambiente
load_dotenv()

async def test_ai_models():
    """Testa os modelos AI corrigidos"""
    print("🧪 [TEST] Iniciando teste dos modelos AI corrigidos...")
    
    # Inicializa o serviço
    ai_service = ProductionMultiAIService()
    
    # Prompt de teste
    test_prompt = """
Context: Sistema de testes de IA
Task: Criar uma resposta curta de teste
Objective: Verificar se os modelos estão funcionando
Situation: Teste automatizado
Target: Desenvolvedores
Audience: Sistema de testes
Response: Resposta de 1-2 frases confirmando que o modelo está funcionando
"""
    
    print(f"📝 [TEST] Prompt de teste: {test_prompt[:100]}...")
    
    try:
        # Testa o serviço
        print("🚀 [TEST] Chamando AI service...")
        result = await ai_service.generate_content(test_prompt)
        
        print("✅ [TEST] Resultado obtido!")
        print(f"🤖 [TEST] Provider: {result.get('provider', 'unknown')}")
        print(f"📏 [TEST] Tamanho: {len(result.get('content', ''))} caracteres")
        print(f"🎨 [TEST] Preview: {result.get('content', '')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ [TEST] Erro no teste: {str(e)}")
        print(f"🔧 [TEST] Tipo do erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    # Executa o teste
    success = asyncio.run(test_ai_models())
    
    if success:
        print("\n🎉 [TEST] Teste concluído com SUCESSO!")
        print("✅ [TEST] Os modelos AI estão funcionando corretamente")
    else:
        print("\n💥 [TEST] Teste FALHOU!")
        print("❌ [TEST] Há problemas com os modelos AI")