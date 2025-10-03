#!/usr/bin/env python3
"""
Teste para verificar se os problemas foram corrigidos
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.integrated_data_service import get_data_service
from app.services.auth_service import AuthService

async def test_fixes():
    print("🔧 TESTANDO CORREÇÕES DOS PROBLEMAS")
    print("="*50)
    
    # 1. Teste do problema de migrations (404)
    print("1. Testando correção do problema de migrations...")
    try:
        data_service = get_data_service()
        
        if hasattr(data_service, 'supabase_service') and data_service.supabase_service:
            # Testa conexão - não deve mais dar 404
            status = await data_service.test_connection()
            if status.get('connected'):
                print("   ✅ Conexão Supabase funcionando sem erro 404")
            else:
                print("   ❌ Problema de conexão ainda existe")
        else:
            print("   ⚠️  Supabase service não disponível")
            
    except Exception as e:
        print(f"   ❌ Erro no teste de conexão: {e}")
    
    # 2. Teste do problema de username 
    print("\n2. Testando correção do problema de username...")
    try:
        auth_service = AuthService()
        
        # Simula um usuário
        test_users = auth_service._load_users()
        if test_users:
            # Pega o primeiro usuário
            user_id = list(test_users.keys())[0]
            user_data = test_users[user_id]
            
            # Converte para objeto User
            user = auth_service._dict_to_user(user_data)
            
            # Testa se o atributo username funciona
            username = user.username
            print(f"   ✅ Username funcionando: '{username}'")
            
            # Testa conversão para dict
            user_dict = user.to_dict()
            if 'username' in user_dict:
                print(f"   ✅ Username no dict: '{user_dict['username']}'")
            else:
                print("   ❌ Username não foi incluído no dict")
                
        else:
            print("   ⚠️  Nenhum usuário encontrado para teste")
            
    except Exception as e:
        print(f"   ❌ Erro no teste de username: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    print("🎉 TESTE DE CORREÇÕES CONCLUÍDO!")

def main():
    asyncio.run(test_fixes())

if __name__ == "__main__":
    main()