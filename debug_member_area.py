#!/usr/bin/env python3
"""
Debug da área de membros - teste de endpoints
"""

import requests
import json

def test_member_area():
    """Testa endpoints da área de membros"""
    
    print("🔧 Debug da área de membros")
    print("=" * 50)
    
    # Login como usuário normal
    print("\n1. 🔐 Fazendo login como usuário admin...")
    login_response = requests.post('http://localhost:8000/api/members/auth/login', json={
        'email': 'admin@costar.com',
        'password': 'admin123'
    })
    
    print(f"Status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.text}")
        return False
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login realizado com sucesso")
    
    # Testar endpoints
    endpoints = [
        ('/api/members/profile', 'Perfil do usuário'),
        ('/api/members/prompts', 'Prompts salvos'),
        ('/api/members/analytics', 'Analytics/Dashboard'),
        ('/api/members/templates', 'Templates do usuário'),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n2. 📡 Testando {description}...")
        print(f"   Endpoint: {endpoint}")
        
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso - Dados recebidos")
                
                # Mostrar estrutura dos dados
                if isinstance(data, dict):
                    print(f"   📋 Estrutura: {list(data.keys())}")
                    if endpoint == '/api/members/profile':
                        print(f"      Username: {data.get('username', 'N/A')}")
                        print(f"      Email: {data.get('email', 'N/A')}")
                        print(f"      Plan: {data.get('subscription_plan', 'N/A')}")
                elif isinstance(data, list):
                    print(f"   📋 Array com {len(data)} items")
                    if len(data) > 0:
                        print(f"   📋 Primeiro item: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
                else:
                    print(f"   📋 Tipo: {type(data)}")
                    
            elif response.status_code == 404:
                print(f"   ❌ Endpoint não encontrado")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   📋 Resposta: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Erro de conexão: {str(e)}")

if __name__ == "__main__":
    test_member_area()