#!/usr/bin/env python3
"""
Debug da role do usuário
"""
import requests
import json

def debug_user_role():
    """Debug da role do usuário após login"""
    print('🔍 DEBUG DA ROLE DO USUÁRIO')
    print('='*40)

    # Login
    data = {
        'email': 'admin@costar.com',
        'password': 'admin123'
    }

    try:
        response = requests.post('http://localhost:8000/api/members/auth/login', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.ok:
            result = response.json()
            user = result.get('user', {})
            token = result.get('access_token', '')
            
            print(f'👤 Email: {user.get("email")}')
            print(f'👑 Role: {user.get("role")} (tipo: {type(user.get("role"))})')
            print(f'📛 Username: {user.get("username")}')
            
            # Testar endpoint /auth/me para verificar dados do token
            me_response = requests.get('http://localhost:8000/api/members/auth/me',
                                     headers={'Authorization': f'Bearer {token}'},
                                     timeout=10)
            
            print(f'\n📋 Endpoint /auth/me Status: {me_response.status_code}')
            if me_response.ok:
                me_data = me_response.json()
                print(f'👤 Email no token: {me_data.get("email")}')
                print(f'👑 Role no token: {me_data.get("role")} (tipo: {type(me_data.get("role"))})')
                print(f'🆔 ID no token: {me_data.get("id")}')
            else:
                print(f'❌ Erro no /auth/me: {me_response.text}')
        
        else:
            print(f'❌ Erro no login: {response.text}')
        
    except Exception as e:
        print(f'❌ Erro: {e}')

if __name__ == "__main__":
    debug_user_role()