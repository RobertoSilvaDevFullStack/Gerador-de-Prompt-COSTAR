#!/usr/bin/env python3
"""
Debug específico dos problemas da área de membros
"""

import requests
import json

def debug_member_area_complete():
    """Debug completo da área de membros"""
    
    print("🔧 Debug completo - Área de Membros")
    print("=" * 60)
    
    # Login admin (sabemos que funciona)
    print("\n1. 🔐 Fazendo login...")
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
    
    # 2. Testar profile endpoint
    print("\n2. 👤 Testando endpoint profile...")
    profile_response = requests.get('http://localhost:8000/api/members/profile', headers=headers)
    print(f"Status: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print("✅ Profile carregado com sucesso")
        print(f"📋 Estrutura: {list(profile_data.keys())}")
        
        # Verificar se tem os dados esperados pelo frontend
        profile = profile_data.get('profile', {})
        print(f"📊 Dados do perfil:")
        print(f"   Username: {profile.get('username', 'N/A')}")
        print(f"   Email: {profile.get('email', 'N/A')}")
        print(f"   Plan: {profile.get('subscription_plan', 'N/A')}")
        print(f"   User ID: {profile.get('user_id', 'N/A')}")
        
        # Verificar usage_stats
        usage_stats = profile.get('usage_stats', {})
        print(f"📈 Usage Stats:")
        print(f"   Total prompts: {usage_stats.get('total_prompts', 'N/A')}")
        print(f"   Templates created: {usage_stats.get('templates_created', 'N/A')}")
        
    else:
        print(f"❌ Erro no profile: {profile_response.text}")
    
    # 3. Testar analytics endpoint
    print("\n3. 📊 Testando endpoint analytics...")
    analytics_response = requests.get('http://localhost:8000/api/members/analytics', headers=headers)
    print(f"Status: {analytics_response.status_code}")
    
    if analytics_response.status_code == 200:
        analytics_data = analytics_response.json()
        print("✅ Analytics carregado com sucesso")
        print(f"📋 Estrutura: {list(analytics_data.keys())}")
        print(f"📊 Dados:")
        print(f"   Prompts total: {analytics_data.get('prompts_generated_total', 'N/A')}")
        print(f"   Prompts este mês: {analytics_data.get('prompts_generated_this_month', 'N/A')}")
        print(f"   Prompts salvos: {analytics_data.get('saved_prompts_count', 'N/A')}")
        print(f"   Templates: {analytics_data.get('templates_count', 'N/A')}")
        print(f"   Membro desde: {analytics_data.get('member_since', 'N/A')}")
    else:
        print(f"❌ Erro no analytics: {analytics_response.text}")
    
    # 4. Testar saved-prompts endpoint
    print("\n4. 💾 Testando endpoint saved-prompts...")
    saved_prompts_response = requests.get('http://localhost:8000/api/members/saved-prompts', headers=headers)
    print(f"Status: {saved_prompts_response.status_code}")
    
    if saved_prompts_response.status_code == 200:
        saved_prompts_data = saved_prompts_response.json()
        print("✅ Saved prompts carregado com sucesso")
        print(f"📋 Estrutura: {list(saved_prompts_data.keys())}")
        print(f"📊 Total: {saved_prompts_data.get('total', 'N/A')}")
        print(f"📊 Prompts: {len(saved_prompts_data.get('prompts', []))} items")
    else:
        print(f"❌ Erro no saved-prompts: {saved_prompts_response.text}")
    
    # 5. Testar quota endpoint
    print("\n5. 📈 Testando endpoint quota...")
    quota_response = requests.get('http://localhost:8000/api/members/quota', headers=headers)
    print(f"Status: {quota_response.status_code}")
    
    if quota_response.status_code == 200:
        quota_data = quota_response.json()
        print("✅ Quota carregado com sucesso")
        print(f"📋 Dados: {quota_data}")
    else:
        print(f"❌ Erro no quota: {quota_response.text}")
        
    # 6. Testar templates endpoint
    print("\n6. 📄 Testando endpoint templates...")
    templates_response = requests.get('http://localhost:8000/api/members/templates', headers=headers)
    print(f"Status: {templates_response.status_code}")
    
    if templates_response.status_code == 200:
        templates_data = templates_response.json()
        print("✅ Templates carregado com sucesso")
        print(f"📋 Estrutura: {list(templates_data.keys())}")
        print(f"📊 Total: {templates_data.get('total', 'N/A')}")
        print(f"📊 Templates: {len(templates_data.get('templates', []))} items")
    else:
        print(f"❌ Erro no templates: {templates_response.text}")
    
    print("\n" + "=" * 60)
    print("✅ Debug completo da área de membros finalizado!")
    
    return True

if __name__ == "__main__":
    debug_member_area_complete()