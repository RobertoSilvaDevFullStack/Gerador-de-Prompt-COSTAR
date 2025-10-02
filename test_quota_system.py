#!/usr/bin/env python3
"""
Script de teste para o sistema de quota e área de membros
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_member_system():
    """Testa o sistema de membros e quota"""
    
    print("🧪 Testando Sistema de Quota de Membros")
    print("=" * 50)
    
    # 1. Testar endpoints sem autenticação (devem falhar)
    print("\n1. Testando acesso sem autenticação...")
    
    endpoints_protegidos = [
        "/api/members/analytics",
        "/api/members/quota", 
        "/api/members/saved-prompts",
        "/api/members/generate-prompt"
    ]
    
    for endpoint in endpoints_protegidos:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: Status {response.status_code} - {'✅ Protegido' if response.status_code == 401 else '❌ Não protegido'}")
        except Exception as e:
            print(f"   {endpoint}: Erro - {e}")
    
    # 2. Testar criação de usuário teste
    print("\n2. Testando criação de usuário...")
    
    user_data = {
        "username": "teste_quota",
        "email": "teste@quota.com", 
        "password": "123456",
        "subscription_plan": "free"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/members/auth/register", json=user_data)
        print(f"   Registro: Status {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Usuário criado com sucesso")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro no registro: {e}")
    
    # 3. Testar login
    print("\n3. Testando login...")
    
    login_data = {
        "username": "teste_quota",
        "password": "123456"
    }
    
    token = None
    try:
        response = requests.post(f"{BASE_URL}/api/members/auth/login", json=login_data)
        print(f"   Login: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("   ✅ Login realizado com sucesso")
            print(f"   Token: {token[:20]}..." if token else "   ❌ Token não recebido")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro no login: {e}")
    
    if not token:
        print("❌ Não foi possível obter token. Parando teste.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Testar endpoints autenticados
    print("\n4. Testando endpoints autenticados...")
    
    # Analytics
    try:
        response = requests.get(f"{BASE_URL}/api/members/analytics", headers=headers)
        print(f"   Analytics: Status {response.status_code}")
        if response.status_code == 200:
            analytics = response.json()
            print(f"   - Prompts totais: {analytics.get('prompts_generated_total', 0)}")
            print(f"   - Prompts este mês: {analytics.get('prompts_generated_this_month', 0)}")
            print(f"   - Prompts salvos: {analytics.get('saved_prompts_count', 0)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro analytics: {e}")
    
    # Quota
    try:
        response = requests.get(f"{BASE_URL}/api/members/quota", headers=headers)
        print(f"   Quota: Status {response.status_code}")
        if response.status_code == 200:
            quota = response.json()
            print(f"   - Usado: {quota.get('used', 0)}")
            print(f"   - Limite: {quota.get('limit', 'N/A')}")
            print(f"   - Permitido: {quota.get('allowed', False)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro quota: {e}")
    
    # 5. Testar geração de prompt
    print("\n5. Testando geração de prompt...")
    
    prompt_data = {
        "contexto": "Sistema de testes automatizados",
        "objetivo": "Testar o sistema de quota de prompts",
        "estilo": "profissional",
        "tom": "neutro",
        "audiencia": "desenvolvedores",
        "formato_resposta": "texto estruturado"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/members/generate-prompt", json=prompt_data, headers=headers)
        print(f"   Geração: Status {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Prompt gerado com sucesso")
            print(f"   - Tokens estimados: {result.get('metadata', {}).get('tokens_estimated', 0)}")
            quota_info = result.get('metadata', {}).get('quota_info', {})
            print(f"   - Quota após geração: {quota_info.get('used', 0)}/{quota_info.get('limit', 'N/A')}")
        elif response.status_code == 429:
            print("   ⚠️ Quota excedida (esperado após múltiplas gerações)")
            quota_info = response.json().get('detail', {}).get('quota_info', {})
            print(f"   - Quota atual: {quota_info.get('used', 0)}/{quota_info.get('limit', 'N/A')}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro geração: {e}")
    
    # 6. Testar múltiplas gerações para verificar quota
    print("\n6. Testando múltiplas gerações (verificação de quota)...")
    
    for i in range(3):
        try:
            response = requests.post(f"{BASE_URL}/api/members/generate-prompt", json=prompt_data, headers=headers)
            print(f"   Tentativa {i+1}: Status {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                quota_info = result.get('metadata', {}).get('quota_info', {})
                print(f"     Quota: {quota_info.get('used', 0)}/{quota_info.get('limit', 'N/A')}")
            elif response.status_code == 429:
                print("     ⚠️ Quota excedida")
                break
                
        except Exception as e:
            print(f"     Erro: {e}")
    
    # 7. Testar salvamento de prompt
    print("\n7. Testando salvamento de prompt...")
    
    save_data = {
        "title": "Prompt de Teste Automatizado",
        "content": "Este é um prompt gerado automaticamente para testar o sistema de salvamento.",
        "context": "Contexto de teste",
        "category": "teste"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/members/save-prompt", json=save_data, headers=headers)
        print(f"   Salvamento: Status {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Prompt salvo com sucesso")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro salvamento: {e}")
    
    # 8. Testar listagem de prompts salvos
    print("\n8. Testando listagem de prompts salvos...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/members/saved-prompts", headers=headers)
        print(f"   Listagem: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            prompts = data.get('prompts', [])
            print(f"   ✅ {len(prompts)} prompts salvos encontrados")
            for i, prompt in enumerate(prompts[:3]):  # Mostrar apenas os 3 primeiros
                print(f"     {i+1}. {prompt.get('title', 'Sem título')} ({prompt.get('created_at', 'N/A')})")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro listagem: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste finalizado!")

if __name__ == "__main__":
    test_member_system()