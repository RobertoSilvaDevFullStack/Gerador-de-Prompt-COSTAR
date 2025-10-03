#!/usr/bin/env python3
"""
🧪 Script de Teste do Sistema Multi-IA
Valida configuração e conectividade de todas as APIs
"""

import os
import sys
import asyncio
from pathlib import Path

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.multi_ai_service import MultiAIService
import json

async def test_multi_ai_system():
    """Testa o sistema Multi-IA completo"""
    
    print("🧪 INICIANDO TESTE DO SISTEMA MULTI-IA")
    print("=" * 50)
    
    # Inicializar serviço
    try:
        multi_ai = MultiAIService()
        await multi_ai.initialize()
        print("✅ Serviço Multi-IA inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar serviço: {e}")
        return False
    
    # Verificar configuração
    print(f"\n📊 CONFIGURAÇÃO DETECTADA:")
    print(f"   Total de provedores configurados: {len(multi_ai.providers)}")
    
    for provider in multi_ai.providers:
        status = "🟢 ATIVO" if provider.is_active else "🔴 INATIVO"
        print(f"   - {provider.name.upper()}: {status}")
    
    # Testar conectividade
    print(f"\n🔍 TESTANDO CONECTIVIDADE:")
    
    test_prompt = "Gere um prompt COSTAR para: criar conteúdo sobre inteligência artificial"
    
    for provider in multi_ai.providers:
        if not provider.is_active:
            print(f"   - {provider.name.upper()}: ⏭️  PULADO (inativo)")
            continue
            
        try:
            print(f"   - {provider.name.upper()}: 🔄 Testando...")
            
            # Simular chamada usando o método unificado
            result = await multi_ai.test_provider_connectivity(provider)
            
            if result:
                print(f"   - {provider.name.upper()}: ✅ FUNCIONANDO")
                provider.success_count += 1
            else:
                print(f"   - {provider.name.upper()}: ❌ FALHOU NO TESTE")
                
        except Exception as e:
            print(f"   - {provider.name.upper()}: ❌ ERRO - {str(e)[:50]}...")
            provider.error_count += 1
    
    # Testar sistema de failover
    print(f"\n🔄 TESTANDO SISTEMA DE FAILOVER:")
    
    try:
        result = await multi_ai.generate_costar_prompt(
            context="Teste de failover",
            objective="Verificar troca automática de IA",
            style="Técnico",
            tone="Profissional", 
            audience="Desenvolvedores",
            response_format="Estruturado"
        )
        
        if result:
            print("✅ Sistema de failover funcionando")
            print(f"   Resultado (primeiros 100 chars): {result[:100]}...")
        else:
            print("❌ Sistema de failover falhou")
            
    except Exception as e:
        print(f"❌ Erro no teste de failover: {e}")
    
    # Mostrar estatísticas
    print(f"\n📈 ESTATÍSTICAS FINAIS:")
    
    total_success = sum(p.success_count for p in multi_ai.providers)
    total_errors = sum(p.error_count for p in multi_ai.providers)
    
    print(f"   Total de sucessos: {total_success}")
    print(f"   Total de erros: {total_errors}")
    
    if total_success > 0:
        success_rate = (total_success / (total_success + total_errors)) * 100
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
    
    # Próximo provedor disponível
    next_provider = multi_ai.get_next_available_provider()
    if next_provider:
        print(f"   Próximo provedor: {next_provider.name.upper()}")
    else:
        print("   ⚠️  Nenhum provedor disponível")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    
    return total_success > 0

def check_environment():
    """Verifica variáveis de ambiente"""
    
    print("🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE:")
    print("-" * 40)
    
    env_vars = [
        "GROQ_API_KEY",
        "GEMINI_API_KEY", 
        "HUGGINGFACE_API_KEY",
        "COHERE_API_KEY",
        "TOGETHER_API_KEY"
    ]
    
    configured = 0
    
    for var in env_vars:
        value = os.getenv(var)
        # Verificar se é uma chave real (não placeholder)
        if value and not any(placeholder in value.lower() for placeholder in [
            "your_key_here", "your_", "_here", "xxxxxx", "api_key_here"
        ]) and len(value) > 10:
            print(f"✅ {var}: Configurada")
            configured += 1
        else:
            print(f"❌ {var}: Não configurada")
    
    print(f"\n📊 APIs configuradas: {configured}/{len(env_vars)}")
    
    if configured == 0:
        print("\n⚠️  ATENÇÃO: Nenhuma API configurada!")
        print("Configure pelo menos uma API no arquivo .env")
        return False
    elif configured == 1:
        print("\n✅ Uma API configurada - Sistema funcionará com capacidade limitada")
        print("💡 RECOMENDAÇÃO: Configure pelo menos 2 APIs para redundância")
    elif configured < 3:
        print("\n✅ Configuração boa para sistema Multi-IA")
        print("💡 SUGESTÃO: Configure mais APIs para máxima disponibilidade")
    else:
        print("\n✅ Configuração excelente para sistema Multi-IA")
    
    return True

if __name__ == "__main__":
    print("🤖 TESTE DO SISTEMA MULTI-IA")
    print("=" * 50)
    
    # Verificar ambiente
    if not check_environment():
        print("\n❌ Teste cancelado devido a problemas de configuração")
        sys.exit(1)
    
    print("\n")
    
    # Executar teste assíncrono
    success = asyncio.run(test_multi_ai_system())
    
    if success:
        print("\n🎉 SISTEMA MULTI-IA FUNCIONANDO CORRETAMENTE!")
        sys.exit(0)
    else:
        print("\n❌ PROBLEMAS DETECTADOS NO SISTEMA MULTI-IA")
        sys.exit(1)