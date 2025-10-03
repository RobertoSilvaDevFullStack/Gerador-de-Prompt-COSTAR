#!/usr/bin/env python3
"""
Script para criar usuário administrador no Supabase
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.supabase_auth_service import SupabaseAuthService
import getpass

def create_admin_user():
    """Criar usuário administrador"""
    print("🔐 CRIAÇÃO DE USUÁRIO ADMINISTRADOR NO SUPABASE")
    print("="*55)
    
    auth_service = SupabaseAuthService()
    
    if not auth_service.enabled:
        print("❌ Supabase não está configurado!")
        print("   Configure as variáveis SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no .env")
        return False
    
    print("✅ Supabase conectado com sucesso!")
    print()
    
    # Obter dados do admin
    email = input("📧 Email do administrador: ").strip()
    if not email or '@' not in email:
        print("❌ Email inválido!")
        return False
    
    name = input("👤 Nome completo (Admin): ").strip() or "Administrator"
    
    password = getpass.getpass("🔒 Senha: ").strip()
    if len(password) < 6:
        print("❌ Senha deve ter pelo menos 6 caracteres!")
        return False
    
    confirm_password = getpass.getpass("🔒 Confirme a senha: ").strip()
    if password != confirm_password:
        print("❌ Senhas não coincidem!")
        return False
    
    print(f"\n📋 Criando usuário admin:")
    print(f"   Email: {email}")
    print(f"   Nome: {name}")
    print(f"   Tipo: Administrador")
    
    confirm = input("\n❓ Confirma a criação? (s/n): ").strip().lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada!")
        return False
    
    # Criar usuário
    admin_user = auth_service.create_admin_user(email, password, name)
    
    if admin_user:
        print("\n🎉 USUÁRIO ADMIN CRIADO COM SUCESSO!")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Nome: {admin_user.username}")
        print(f"   Role: {admin_user.role.value}")
        print("\n✅ Agora você pode fazer login no sistema!")
        return True
    else:
        print("\n❌ Erro ao criar usuário admin!")
        return False

def test_admin_login():
    """Testar login do admin"""
    print("\n🔍 TESTANDO LOGIN DO ADMIN")
    print("="*30)
    
    auth_service = SupabaseAuthService()
    
    email = input("📧 Email: ").strip()
    password = getpass.getpass("🔒 Senha: ").strip()
    
    token = auth_service.authenticate_user(email, password)
    
    if token:
        print("✅ Login realizado com sucesso!")
        print(f"🎫 Token gerado: {token[:50]}...")
        
        # Buscar usuário para validar
        user = auth_service.get_user_by_email(email)
        if user:
            print(f"👤 Usuário: {user.username} ({user.role.value})")
        
        return True
    else:
        print("❌ Falha no login!")
        return False

def list_all_users():
    """Listar todos os usuários"""
    print("\n📋 LISTA DE USUÁRIOS")
    print("="*25)
    
    auth_service = SupabaseAuthService()
    users = auth_service.get_all_users()
    
    if not users:
        print("⚠️  Nenhum usuário encontrado")
        return
    
    print(f"📊 Total: {len(users)} usuário(s)")
    print()
    
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
        print(f"   Role: {user.get('role', 'N/A')} | Ativo: {user.get('is_active', False)}")
        print(f"   ID: {user.get('id', 'N/A')}")
        print()

def main():
    """Função principal"""
    while True:
        print("\n🎯 MENU DE ADMINISTRAÇÃO SUPABASE")
        print("="*35)
        print("1. Criar usuário administrador")
        print("2. Testar login de admin")
        print("3. Listar todos os usuários")
        print("0. Sair")
        
        choice = input("\n👆 Escolha uma opção: ").strip()
        
        if choice == '1':
            create_admin_user()
        elif choice == '2':
            test_admin_login()
        elif choice == '3':
            list_all_users()
        elif choice == '0':
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()