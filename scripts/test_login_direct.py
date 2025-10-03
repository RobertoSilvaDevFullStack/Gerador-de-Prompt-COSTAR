#!/usr/bin/env python3
"""
Teste de login direto - COSTAR AI
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.supabase_auth_service import SupabaseAuthService
import logging

# Reduzir logs
logging.getLogger().setLevel(logging.WARNING)

def test_login():
    """Teste direto de login"""
    print("🔐 TESTE DE LOGIN DIRETO - COSTAR AI")
    print("="*45)
    
    # Inicializar serviço
    auth_service = SupabaseAuthService()
    
    if not auth_service.enabled:
        print("❌ Supabase não configurado!")
        return False
    
    print("✅ Supabase conectado")
    
    # Credenciais para teste
    email = "admin@costar.com"
    password = "admin123"
    
    print(f"\n📧 Testando login: {email}")
    print(f"🔒 Senha: {password}")
    
    # Fazer login
    token = auth_service.authenticate_user(email, password)
    
    if token:
        print(f"\n✅ LOGIN BEM-SUCEDIDO!")
        print(f"🎫 Token: {token[:50]}...")
        
        # Verificar usuário
        user = auth_service.get_user_by_email(email)
        if user:
            print(f"\n👤 DADOS DO USUÁRIO:")
            print(f"   📧 Email: {user.email}")
            print(f"   👑 Role: {user.role.value}")
            print(f"   📛 Username: {user.username}")
            print(f"   ✅ Ativo: {user.is_active}")
            print(f"   📅 Criado: {user.created_at}")
            
            # Verificar token
            verified_user = auth_service.verify_token(token)
            if verified_user:
                print(f"\n🔒 TOKEN VÁLIDO ✅")
                print(f"   Verificado para: {verified_user.email}")
            else:
                print(f"\n❌ TOKEN INVÁLIDO")
        
        return True
    else:
        print(f"\n❌ FALHA NO LOGIN")
        
        # Verificar se usuário existe
        user = auth_service.get_user_by_email(email)
        if user:
            print(f"   👤 Usuário existe: {user.email}")
            print(f"   ✅ Ativo: {user.is_active}")
            print(f"   🔑 Role: {user.role.value}")
            print("   ⚠️  Problema: Senha incorreta")
        else:
            print("   ❌ Usuário não encontrado")
        
        return False

def list_users():
    """Listar usuários do sistema"""
    print("\n" + "="*45)
    print("👥 USUÁRIOS NO SISTEMA")
    print("="*45)
    
    auth_service = SupabaseAuthService()
    users = auth_service.get_all_users()
    
    if users:
        print(f"📊 Total: {len(users)} usuário(s)")
        print()
        
        for i, user in enumerate(users, 1):
            email = user.get('email', 'N/A')
            role = user.get('role', 'N/A')
            is_active = user.get('is_active', False)
            username = user.get('username', 'N/A')
            
            status = "🟢" if is_active else "🔴"
            role_icon = "👑" if role == "admin" else "👤"
            
            print(f"{i}. {role_icon} {username}")
            print(f"   📧 {email}")
            print(f"   🔑 {role} {status}")
            print()
    else:
        print("⚠️  Nenhum usuário encontrado")

def main():
    """Função principal"""
    # Testar login
    login_success = test_login()
    
    # Listar usuários
    list_users()
    
    if login_success:
        print("🎉 SISTEMA DE LOGIN FUNCIONANDO!")
        print("\n📋 INSTRUÇÕES PARA USO:")
        print("1. Execute: python main_demo.py")
        print("2. Acesse: http://localhost:8000")
        print("3. Clique em 'Login'")
        print("4. Use as credenciais:")
        print("   📧 Email: admin@costar.com")
        print("   🔒 Senha: admin123")
        print("5. Será redirecionado para dashboard admin")
    else:
        print("❌ PROBLEMAS NO LOGIN!")
        print("Execute: python scripts/create_admin_user_supabase.py")

if __name__ == "__main__":
    main()