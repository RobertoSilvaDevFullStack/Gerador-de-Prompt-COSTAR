#!/usr/bin/env python3
"""
Teste direto da função get_admin_user
"""
import sys
sys.path.append('.')

from app.services.supabase_auth_service import SupabaseAuthService

def test_admin_user_directly():
    """Teste direto do usuário admin"""
    print('🔍 TESTE DIRETO DO USUÁRIO ADMIN')
    print('='*40)
    
    auth_service = SupabaseAuthService()
    
    # Fazer login direto
    user = auth_service.authenticate_user('admin@costar.com', 'admin123')
    
    if user:
        print(f'✅ Usuário encontrado:')
        print(f'  📧 Email: {user.email}')
        print(f'  👑 Role: "{user.role}" (tipo: {type(user.role)})')
        print(f'  📛 Username: {user.username}')
        print(f'  🆔 ID: {user.id}')
        
        # Testar comparações
        from app.services.supabase_auth_service import UserRole
        
        print(f'\n🔍 COMPARAÇÕES:')
        print(f'  user.role == "admin": {user.role == "admin"}')
        print(f'  user.role == UserRole.ADMIN.value: {user.role == UserRole.ADMIN.value}')
        print(f'  user.role == str(UserRole.ADMIN): {user.role == str(UserRole.ADMIN)}')
        print(f'  "UserRole.ADMIN" in user.role: {"UserRole.ADMIN" in str(user.role)}')
        
        print(f'\n📊 VALORES:')
        print(f'  UserRole.ADMIN: {UserRole.ADMIN}')
        print(f'  UserRole.ADMIN.value: {UserRole.ADMIN.value}')
        print(f'  str(UserRole.ADMIN): {str(UserRole.ADMIN)}')
        
    else:
        print('❌ Usuário não encontrado')

if __name__ == "__main__":
    test_admin_user_directly()