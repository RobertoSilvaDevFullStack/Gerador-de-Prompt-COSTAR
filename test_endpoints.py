#!/usr/bin/env python3
"""
Script simples para testar os endpoints da área de membros
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_login_and_endpoints():
    """Testa login e endpoints"""
    
    print("🔐 Fazendo login...")
    
    # Login
    login_data = {
        "email": "admin@costar.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/members/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Testar analytics
            print("\n📊 Testando Analytics...")
            analytics_response = requests.get(f"{BASE_URL}/api/members/analytics", headers=headers)
            print(f"Analytics Status: {analytics_response.status_code}")
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                print(f"Analytics: {json.dumps(analytics_data, indent=2)}")
            else:
                print(f"Erro: {analytics_response.text}")
            
            # Testar quota
            print("\n🎯 Testando Quota...")
            quota_response = requests.get(f"{BASE_URL}/api/members/quota", headers=headers)
            print(f"Quota Status: {quota_response.status_code}")
            if quota_response.status_code == 200:
                quota_data = quota_response.json()
                print(f"Quota: {json.dumps(quota_data, indent=2)}")
            else:
                print(f"Erro: {quota_response.text}")
            
            # Testar prompts salvos
            print("\n💾 Testando Prompts Salvos...")
            prompts_response = requests.get(f"{BASE_URL}/api/members/saved-prompts", headers=headers)
            print(f"Prompts Status: {prompts_response.status_code}")
            if prompts_response.status_code == 200:
                prompts_data = prompts_response.json()
                print(f"Prompts: {json.dumps(prompts_data, indent=2)}")
            else:
                print(f"Erro: {prompts_response.text}")
                
        else:
            print(f"❌ Erro no login: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_login_and_endpoints()