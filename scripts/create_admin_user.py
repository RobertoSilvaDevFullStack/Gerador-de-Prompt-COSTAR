#!/usr/bin/env python3
"""
Script para criar usuário administrador padrão
"""

import os
import sys
import json
import hashlib
import uuid
from datetime import datetime

def create_admin_user():
    """Criar usuário administrador padrão"""
    
    # Garantir que o diretório data existe
    os.makedirs('data', exist_ok=True)
    
    # Carregar usuários existentes
    users_file = 'data/users.json'
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
    
    # Verificar se admin já existe
    admin_exists = any(
        user.get('email') == 'admin@costar.com' 
        for user in users.values()
    )
    
    if admin_exists:
        print("✅ Usuário admin já existe!")
        return
    
    # Criar usuário admin
    admin_id = str(uuid.uuid4())
    admin_password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    
    admin_user = {
        'id': admin_id,
        'email': 'admin@costar.com',
        'password_hash': admin_password_hash,
        'role': 'admin',
        'created_at': datetime.now().isoformat(),
        'last_login': None,
        'is_active': True,
        'profile': {
            'name': 'Administrador',
            'company': 'COSTAR System',
            'preferences': {
                'default_style': 'Profissional',
                'default_tone': 'Formal',
                'favorite_use_cases': ['admin', 'analytics']
            }
        }
    }
    
    # Salvar usuário
    users[admin_id] = admin_user
    
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    print("🎉 Usuário administrador criado com sucesso!")
    print("📧 Email: admin@costar.com")
    print("🔑 Senha: admin123")
    print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")

if __name__ == "__main__":
    create_admin_user()