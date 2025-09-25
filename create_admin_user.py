#!/usr/bin/env python3
"""
Script para criar usuário administrador
"""

import os
import sys
from datetime import datetime
from services.auth_service import AuthService, UserRole

def create_admin_user():
    """Criar usuário administrador"""
    print("🔧 CRIANDO USUÁRIO ADMINISTRADOR")
    print("=" * 40)
    
    # Inicializar serviço de autenticação
    auth_service = AuthService()
    
    # Dados do admin
    admin_email = "admin@costar.com"
    admin_password = "admin123"  # Senha temporária
    
    # Verificar se admin já existe
    existing_admin = auth_service.get_user_by_email(admin_email)
    if existing_admin:
        print(f"⚠️  Admin já existe: {admin_email}")
        print(f"🔑 Use a senha: {admin_password}")
        return existing_admin
    
    # Criar usuário admin
    admin_user = auth_service.register_user(
        email=admin_email,
        password=admin_password,
        role=UserRole.ADMIN
    )
    
    if admin_user:
        print("✅ Usuário administrador criado com sucesso!")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Senha: {admin_password}")
        print(f"👤 ID: {admin_user.id}")
        print(f"🎭 Role: {admin_user.role.value}")
        
        # Gerar token para teste
        token = auth_service.authenticate_user(admin_email, admin_password)
        if token:
            print(f"🎫 Token JWT gerado com sucesso")
            print(f"Token (primeiros 50 chars): {token[:50]}...")
        
        print("\n📋 INFORMAÇÕES DE ACESSO:")
        print(f"🌐 URL Login: http://localhost:8000/member-area.html")
        print(f"🎛️  Dashboard Admin: http://localhost:8000/admin-dashboard.html")
        
        return admin_user
    else:
        print("❌ Erro ao criar usuário administrador!")
        return None

def create_test_users():
    """Criar usuários de teste"""
    print("\n🧪 CRIANDO USUÁRIOS DE TESTE")
    print("=" * 40)
    
    auth_service = AuthService()
    
    test_users = [
        {
            "email": "user@test.com",
            "password": "user123",
            "role": UserRole.FREE,
            "name": "Usuário Teste"
        },
        {
            "email": "premium@test.com", 
            "password": "premium123",
            "role": UserRole.PREMIUM,
            "name": "Usuário Premium"
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        existing = auth_service.get_user_by_email(user_data["email"])
        if existing:
            print(f"⚠️  Usuário já existe: {user_data['email']}")
            created_users.append(existing)
            continue
            
        user = auth_service.register_user(
            email=user_data["email"],
            password=user_data["password"],
            role=user_data["role"]
        )
        
        if user:
            print(f"✅ Criado: {user_data['email']} ({user_data['role'].value})")
            created_users.append(user)
        else:
            print(f"❌ Erro ao criar: {user_data['email']}")
    
    return created_users

if __name__ == "__main__":
    print("🚀 CONFIGURAÇÃO DE USUÁRIOS COSTAR")
    print("=" * 50)
    
    # Criar admin
    admin = create_admin_user()
    
    # Criar usuários de teste
    test_users = create_test_users()
    
    print(f"\n📊 RESUMO:")
    print(f"👨‍💼 Admin criado: {'✅' if admin else '❌'}")
    print(f"🧪 Usuários teste: {len(test_users)}")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("1. Acesse: http://localhost:8000/member-area.html")
    print("2. Faça login com admin@costar.com / admin123")
    print("3. Acesse o dashboard: http://localhost:8000/admin-dashboard.html")
    
    print(f"\n🔐 CREDENCIAIS:")
    print("ADMIN: admin@costar.com / admin123")
    print("USER: user@test.com / user123") 
    print("PREMIUM: premium@test.com / premium123")