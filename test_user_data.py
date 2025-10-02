#!/usr/bin/env python3
"""
Testar login com usuário que tem dados
"""

import requests

def test_user_with_data():
    # Tentar login com usuário que tem dados
    login_response = requests.post('http://localhost:8000/api/members/auth/login', json={
        'email': 'joao.silva@email.com',
        'password': 'senha123'
    })

    print(f'Status login: {login_response.status_code}')
    if login_response.status_code == 200:
        print('✅ Login com João Silva funcionou!')
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Testar analytics deste usuário
        analytics_response = requests.get('http://localhost:8000/api/members/analytics', headers=headers)
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            print(f'Prompts total: {analytics.get("prompts_generated_total", "N/A")}')
            print(f'Prompts salvos: {analytics.get("saved_prompts_count", "N/A")}')
            print(f'Templates: {analytics.get("templates_count", "N/A")}')
        else:
            print(f'❌ Erro analytics: {analytics_response.text}')
            
        # Verificar prompts salvos
        saved_prompts_response = requests.get('http://localhost:8000/api/members/saved-prompts', headers=headers)
        print(f'Saved prompts status: {saved_prompts_response.status_code}')
        if saved_prompts_response.status_code == 200:
            data = saved_prompts_response.json()
            print(f'Total prompts salvos no endpoint: {data.get("total", 0)}')
            prompts = data.get('prompts', [])
            print(f'Lista de prompts: {len(prompts)} items')
            for i, prompt in enumerate(prompts[:3]):
                print(f'  {i+1}. {prompt.get("title", "Sem título")} - {prompt.get("created_at", "N/A")}')
        else:
            print(f'Erro saved-prompts: {saved_prompts_response.text}')
    else:
        print(f'❌ Erro no login: {login_response.text}')

if __name__ == "__main__":
    test_user_with_data()