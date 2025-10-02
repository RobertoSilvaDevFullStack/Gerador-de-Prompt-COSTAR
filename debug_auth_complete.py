#!/usr/bin/env python3
"""
Script para debugar problemas de autenticação e permissões
"""

import requests
import json

BASE_URL = "http://localhost:8000"  # Volta para porta 8000

def test_complete_auth_flow():
    """Testa fluxo completo de autenticação e permissões"""
    
    print("🔐 Testando fluxo completo de autenticação...")
    
    # 1. Login
    login_data = {
        "email": "admin@costar.com", 
        "password": "admin123"
    }
    
    try:
        print("\n1. Fazendo login...")
        response = requests.post(f"{BASE_URL}/api/members/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Erro no login: {response.text}")
            return
            
        data = response.json()
        token = data.get("access_token")
        print(f"   ✅ Token obtido: {token[:30]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Teste de informações do usuário
        print("\n2. Testando informações do usuário...")
        user_response = requests.get(f"{BASE_URL}/api/members/auth/me", headers=headers)
        print(f"   Status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   ✅ Usuário: {user_data.get('email')}")
            print(f"   ✅ Role: {user_data.get('role')}")
            print(f"   📋 Dados completos: {json.dumps(user_data, indent=2)}")
        else:
            print(f"   ❌ Erro: {user_response.text}")
        
        # 3. Teste debug token
        print("\n3. Testando debug do token...")
        debug_response = requests.get(f"{BASE_URL}/api/members/debug/token-info", headers=headers)
        print(f"   Status: {debug_response.status_code}")
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"   ✅ Debug: {json.dumps(debug_data, indent=2)}")
        else:
            print(f"   ❌ Erro: {debug_response.text}")
        
        # 4. Teste área de membros
        print("\n4. Testando área de membros...")
        
        # Analytics
        analytics_response = requests.get(f"{BASE_URL}/api/members/analytics", headers=headers)
        print(f"   Analytics Status: {analytics_response.status_code}")
        if analytics_response.status_code == 200:
            print(f"   ✅ Analytics funcionando")
        else:
            print(f"   ❌ Analytics erro: {analytics_response.text}")
        
        # Quota
        quota_response = requests.get(f"{BASE_URL}/api/members/quota", headers=headers)
        print(f"   Quota Status: {quota_response.status_code}")
        if quota_response.status_code == 200:
            quota_data = quota_response.json()
            print(f"   ✅ Quota: Usado={quota_data.get('used')}, Limite={quota_data.get('limit')}")
        else:
            print(f"   ❌ Quota erro: {quota_response.text}")
        
        # 5. Teste área de admin
        print("\n5. Testando área de admin...")
        admin_response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers=headers)
        print(f"   Admin Dashboard Status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            print(f"   ✅ Admin dashboard funcionando")
            print(f"   📊 Métricas: {json.dumps(admin_data, indent=2)[:200]}...")
        else:
            print(f"   ❌ Admin erro: {admin_response.text}")
            
        # 6. Teste específico de perfil de membro
        print("\n6. Testando perfil de membro...")
        profile_response = requests.get(f"{BASE_URL}/api/members/profile", headers=headers)
        print(f"   Profile Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"   ✅ Perfil: {json.dumps(profile_data, indent=2)}")
        else:
            print(f"   ❌ Perfil erro: {profile_response.text}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_complete_auth_flow()