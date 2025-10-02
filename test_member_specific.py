#!/usr/bin/env python3
"""
Script para testar especificamente prompts salvos e analíticos
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_member_endpoints():
    """Testa endpoints específicos da área de membros"""
    
    print("🧪 Testando endpoints da área de membros...")
    
    # 1. Login
    login_data = {
        "email": "admin@costar.com", 
        "password": "admin123"
    }
    
    try:
        print("\n1. Fazendo login...")
        response = requests.post(f"{BASE_URL}/api/members/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"   ❌ Erro no login: {response.text}")
            return
            
        data = response.json()
        token = data.get("access_token")
        print(f"   ✅ Token obtido")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Teste Analytics (que parece funcionar)
        print("\n2. Testando analytics...")
        analytics_response = requests.get(f"{BASE_URL}/api/members/analytics", headers=headers)
        print(f"   Status: {analytics_response.status_code}")
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"   ✅ Analytics obtidas:")
            print(f"       - Total prompts: {analytics_data.get('prompts_generated_total', 'N/A')}")
            print(f"       - Prompts este mês: {analytics_data.get('prompts_generated_this_month', 'N/A')}")
            print(f"       - Prompts salvos: {analytics_data.get('saved_prompts_count', 'N/A')}")
            print(f"       - Membro desde: {analytics_data.get('member_since', 'N/A')}")
        else:
            print(f"   ❌ Erro: {analytics_response.text}")
        
        # 3. Teste Quota
        print("\n3. Testando quotas...")
        quota_response = requests.get(f"{BASE_URL}/api/members/quota", headers=headers)
        print(f"   Status: {quota_response.status_code}")
        
        if quota_response.status_code == 200:
            quota_data = quota_response.json()
            print(f"   ✅ Quotas obtidas:")
            print(f"       - Usado: {quota_data.get('used', 'N/A')}")
            print(f"       - Limite: {quota_data.get('limit', 'N/A')}")
            print(f"       - Permitido: {quota_data.get('allowed', 'N/A')}")
            print(f"       - Razão: {quota_data.get('reason', 'N/A')}")
        else:
            print(f"   ❌ Erro: {quota_response.text}")
        
        # 4. Teste Prompts Salvos (problema principal)
        print("\n4. Testando prompts salvos...")
        saved_prompts_response = requests.get(f"{BASE_URL}/api/members/saved-prompts", headers=headers)
        print(f"   Status: {saved_prompts_response.status_code}")
        
        if saved_prompts_response.status_code == 200:
            saved_data = saved_prompts_response.json()
            print(f"   ✅ Prompts salvos obtidos:")
            print(f"       - Total: {saved_data.get('total', 'N/A')}")
            print(f"       - Quantidade de prompts: {len(saved_data.get('prompts', []))}")
            if saved_data.get('prompts'):
                for idx, prompt in enumerate(saved_data.get('prompts', [])[:3]):  # Mostra só os 3 primeiros
                    print(f"         {idx+1}. {prompt.get('title', 'Sem título')} - {prompt.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ Erro: {saved_prompts_response.text}")
        
        # 5. Teste Templates (caso exista)
        print("\n5. Testando templates de usuário...")
        templates_response = requests.get(f"{BASE_URL}/api/members/templates", headers=headers)
        print(f"   Status: {templates_response.status_code}")
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            print(f"   ✅ Templates obtidos: {len(templates_data.get('templates', []))} templates")
        else:
            print(f"   ❌ Erro: {templates_response.text}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_member_endpoints()