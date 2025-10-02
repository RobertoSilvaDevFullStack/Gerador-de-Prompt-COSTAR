#!/usr/bin/env python3
"""
Script para testar especificamente os endpoints do dashboard admin
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_dashboard_endpoints():
    """Testa endpoints específicos do dashboard admin"""
    
    print("🔧 Testando endpoints do dashboard admin...")
    
    # 1. Login como admin
    login_data = {
        "email": "admin@costar.com", 
        "password": "admin123"
    }
    
    try:
        print("\n1. Fazendo login admin...")
        response = requests.post(f"{BASE_URL}/api/members/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"   ❌ Erro no login: {response.text}")
            return
            
        data = response.json()
        token = data.get("access_token")
        print(f"   ✅ Token admin obtido")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Teste dashboard admin principal
        print("\n2. Testando /api/admin/dashboard...")
        dashboard_response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers=headers)
        print(f"   Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"   ✅ Dashboard carregado:")
            
            # Overview
            overview = dashboard_data.get('overview', {})
            print(f"       📊 Total usuários: {overview.get('total_users', 'N/A')}")
            print(f"       📊 Usuários ativos 24h: {overview.get('active_users_24h', 'N/A')}")
            print(f"       📊 Total API calls: {overview.get('total_api_calls', 'N/A')}")
            print(f"       📊 API calls 24h: {overview.get('api_calls_24h', 'N/A')}")
            print(f"       📊 Taxa de erro: {overview.get('error_rate_24h', 'N/A')}%")
            print(f"       📊 Tempo resposta: {overview.get('avg_response_time_24h', 'N/A')}ms")
            
            # API Usage
            api_usage = dashboard_data.get('api_usage', {})
            print(f"       📈 Uso da API: {len(api_usage)} entradas")
            
            # User Growth
            user_growth = dashboard_data.get('user_growth', [])
            print(f"       👥 Crescimento usuários: {len(user_growth)} pontos de dados")
            
        else:
            print(f"   ❌ Erro: {dashboard_response.text}")
        
        # 3. Teste de usuários
        print("\n3. Testando /api/admin/users...")
        users_response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        print(f"   Status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"   ✅ Usuários carregados: {len(users_data.get('users', []))} usuários")
            
            for user in users_data.get('users', [])[:3]:  # Primeiros 3
                print(f"       👤 {user.get('username', 'N/A')} ({user.get('email', 'N/A')}) - {user.get('subscription_plan', 'N/A')}")
                
        else:
            print(f"   ❌ Erro: {users_response.text}")
            
        # 4. Teste templates
        print("\n4. Testando /api/admin/templates...")
        templates_response = requests.get(f"{BASE_URL}/api/admin/templates", headers=headers)
        print(f"   Status: {templates_response.status_code}")
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            print(f"   ✅ Templates carregados: {len(templates_data.get('templates', []))} templates")
            
            for template in templates_data.get('templates', [])[:3]:  # Primeiros 3
                print(f"       📄 {template.get('title', 'N/A')} (por {template.get('creator_name', 'N/A')})")
                
        else:
            print(f"   ❌ Erro: {templates_response.text}")
            
        # 5. Verificar se endpoints existem
        print("\n5. Verificando outros endpoints admin...")
        
        test_endpoints = [
            "/api/admin/analytics",
            "/api/admin/system-health",
            "/api/admin/logs"
        ]
        
        for endpoint in test_endpoints:
            try:
                test_response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                print(f"   {endpoint}: Status {test_response.status_code}")
            except Exception as e:
                print(f"   {endpoint}: Erro - {e}")
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_admin_dashboard_endpoints()