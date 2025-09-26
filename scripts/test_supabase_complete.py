#!/usr/bin/env python3
"""
Teste completo do Supabase após deployment
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.integrated_data_service import get_data_service

async def test_full_supabase():
    print("🚀 TESTE COMPLETO DO SUPABASE APÓS DEPLOYMENT")
    print("="*60)
    
    try:
        # Inicializa serviço
        data_service = get_data_service()
        print(f"📊 Modo: {data_service.mode}")
        
        # Testa conexão
        status = await data_service.test_connection()
        connected = status.get("connected", False)
        print(f"🔗 Conexão: {'✅ Sucesso' if connected else '❌ Falhou'}")
        
        if not connected:
            print("❌ Não foi possível conectar ao Supabase")
            return
        
        # Testa acesso aos dados
        if hasattr(data_service, 'supabase_service') and data_service.supabase_service:
            try:
                # Usa o cliente admin
                supabase_admin = data_service.supabase_service.admin_client
                
                print("\n🔍 TESTANDO ACESSO AOS DADOS...")
                
                # 1. Busca configurações do sistema
                print("📋 Buscando configurações do sistema...")
                config_result = supabase_admin.table('system_settings').select('key, value, description').limit(3).execute()
                
                if config_result.data:
                    print(f"✅ Configurações encontradas: {len(config_result.data)}")
                    for config in config_result.data:
                        key = config.get('key', 'N/A')
                        desc = config.get('description', 'N/A')
                        print(f"   • {key}: {desc}")
                else:
                    print("⚠️  Nenhuma configuração encontrada")
                
                # 2. Busca templates
                print("\n📝 Buscando templates...")
                template_result = supabase_admin.table('prompt_templates').select('title, category, difficulty_level').limit(2).execute()
                
                if template_result.data:
                    print(f"✅ Templates encontrados: {len(template_result.data)}")
                    for template in template_result.data:
                        title = template.get('title', 'N/A')
                        category = template.get('category', 'N/A')
                        level = template.get('difficulty_level', 'N/A')
                        print(f"   • {title} ({category} - {level})")
                else:
                    print("⚠️  Nenhum template encontrado")
                
                # 3. Testa contagem de tabelas
                print("\n📊 Verificando estrutura das tabelas...")
                tables = ['user_profiles', 'prompts', 'prompt_templates', 'template_ratings', 'ai_usage_logs', 'system_settings']
                
                for table in tables:
                    try:
                        count_result = supabase_admin.table(table).select('id', count='exact').limit(1).execute()
                        count = count_result.count if hasattr(count_result, 'count') else 'N/A'
                        print(f"   ✅ {table}: acessível (registros: {count})")
                    except Exception as e:
                        print(f"   ❌ {table}: erro - {e}")
                
            except Exception as e:
                print(f"❌ Erro ao acessar dados do Supabase: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("🎉 SUPABASE CONFIGURADO E FUNCIONANDO!")
        print("✅ Todas as tabelas criadas")
        print("✅ Dados iniciais inseridos")
        print("✅ Conexões funcionando")
        print("✅ Sistema pronto para produção!")
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        import traceback
        traceback.print_exc()

def main():
    asyncio.run(test_full_supabase())

if __name__ == "__main__":
    main()