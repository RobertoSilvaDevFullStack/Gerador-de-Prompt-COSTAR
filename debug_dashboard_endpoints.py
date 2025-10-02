#!/usr/bin/env python3
"""
Teste rápido dos endpoints do dashboard
"""

import requests
import json

def test_dashboard_endpoints():
    """Testa os endpoints do dashboard admin"""
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        login_response = requests.post('http://localhost:8000/api/members/auth/login', json={
            'email': 'admin@costar.com',
            'password': 'admin123'
        })

        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False

        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("✅ Login realizado com sucesso")
        
        # Testar dashboard
        print("\n📊 Testando endpoint dashboard...")
        dashboard_response = requests.get('http://localhost:8000/api/admin/dashboard', headers=headers)
        print(f"Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            overview = data.get('overview', {})
            print(f"  ✅ Total usuários: {overview.get('total_users', 'N/A')}")
            print(f"  ✅ API calls: {overview.get('total_api_calls', 'N/A')}")
            print(f"  ✅ Taxa de erro: {overview.get('error_rate_24h', 'N/A')}%")
            print(f"  ✅ Tempo resposta: {overview.get('avg_response_time_24h', 'N/A')}ms")
        else:
            print(f"  ❌ Erro no dashboard: {dashboard_response.text}")
        
        # Testar usuários
        print("\n👥 Testando endpoint usuários...")
        users_response = requests.get('http://localhost:8000/api/admin/users', headers=headers)
        print(f"Status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            users = users_data.get('users', [])
            print(f"  ✅ Quantidade de usuários: {len(users)}")
            
            if len(users) > 0:
                print("  📋 Primeiros usuários:")
                for user in users[:3]:
                    email = user.get('email', 'N/A')
                    plan = user.get('subscription_plan', 'N/A')
                    print(f"    • {email} - {plan}")
        else:
            print(f"  ❌ Erro nos usuários: {users_response.text}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

if __name__ == "__main__":
    test_dashboard_endpoints()