#!/usr/bin/env python3
"""
Teste de login após correções
"""
import requests
import json

def test_login_fixed():
    """Testar login após correções"""
    print('🔐 TESTANDO LOGIN APÓS CORREÇÕES')
    print('='*40)

    data = {
        'email': 'admin@costar.com',
        'password': 'admin123'
    }

    try:
        response = requests.post('http://localhost:8000/api/members/auth/login', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f'Status: {response.status_code}')
        
        if response.ok:
            result = response.json()
            print('✅ LOGIN BEM-SUCEDIDO!')
            token = result.get('access_token', '')
            user = result.get('user', {})
            print(f'🎫 Token: {token[:50]}...')
            print(f'👤 Usuário: {user.get("email", "N/A")}')
            print(f'👑 Role: {user.get("role", "N/A")}')
            print(f'📛 Username: {user.get("username", "N/A")}')
            
            # Testar dashboard admin
            admin_response = requests.get('http://localhost:8000/api/admin/dashboard',
                                         headers={'Authorization': f'Bearer {token}'},
                                         timeout=10)
            print(f'\n📊 Dashboard Status: {admin_response.status_code}')
            if admin_response.ok:
                print('✅ Dashboard admin acessível!')
                
                # Testar informações do usuário
                me_response = requests.get('http://localhost:8000/api/members/auth/me',
                                         headers={'Authorization': f'Bearer {token}'},
                                         timeout=10)
                print(f'👤 User Info Status: {me_response.status_code}')
                if me_response.ok:
                    me_data = me_response.json()
                    print(f'📧 Email confirmado: {me_data.get("email", "N/A")}')
                    print(f'👑 Role confirmada: {me_data.get("role", "N/A")}')
                
                print('\n🎉 SISTEMA DE LOGIN 100% FUNCIONAL!')
                print('💻 Agora você pode acessar:')
                print('   🌐 http://localhost:8000 (Frontend)')
                print('   👥 http://localhost:8000/member-area.html (Área de Membros)')
                print('   🔧 http://localhost:8000/admin-dashboard.html (Dashboard Admin)')
                print('\n🔑 Credenciais:')
                print('   📧 Email: admin@costar.com')
                print('   🔒 Senha: admin123')
            else:
                print(f'❌ Erro no dashboard: {admin_response.text[:200]}')
        else:
            print(f'❌ ERRO NO LOGIN: {response.status_code}')
            print(f'Resposta: {response.text}')
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        print('Verifique se o servidor está rodando em http://localhost:8000')

if __name__ == "__main__":
    test_login_fixed()