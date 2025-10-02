#!/usr/bin/env python3
"""
Teste simulando exatamente o login em produção
"""

import requests
import json

def simulate_production_login():
    """Simula o login exatamente como seria em produção"""
    
    print("🔧 Simulando login em produção")
    print("=" * 50)
    
    # URL base (simular produção)
    base_url = "http://localhost:8000"  # Local para teste
    
    # Dados do usuário com prompts salvos
    email = "joao.silva@email.com"
    password = "senha123"
    
    print(f"\n1. 🔐 Tentando login com {email}...")
    
    # 1. Login
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/members/auth/login", 
                                     json=login_data,
                                     headers={"Content-Type": "application/json"})
        
        print(f"Status login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login:")
            print(f"Resposta: {login_response.text}")
            return False
        
        # Extrair token
        login_result = login_response.json()
        token = login_result.get("access_token")
        
        if not token:
            print("❌ Token não encontrado na resposta")
            print(f"Resposta completa: {login_result}")
            return False
            
        print("✅ Login realizado com sucesso!")
        print(f"Token: {token[:20]}...")
        
        # Headers para próximas requisições
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Simular carregamento da área de membros
        print(f"\n2. 👤 Simulando carregamento do perfil...")
        
        # Perfil
        profile_response = requests.get(f"{base_url}/api/members/profile", headers=headers)
        print(f"Profile status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            profile = profile_data.get("profile", {})
            print(f"✅ Perfil carregado: {profile.get('username')} ({profile.get('email')})")
        else:
            print(f"❌ Erro no perfil: {profile_response.text}")
        
        # Analytics (dashboard)
        print(f"\n3. 📊 Simulando carregamento do dashboard...")
        analytics_response = requests.get(f"{base_url}/api/members/analytics", headers=headers)
        print(f"Analytics status: {analytics_response.status_code}")
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"✅ Analytics carregado:")
            print(f"   Prompts total: {analytics_data.get('prompts_generated_total', 0)}")
            print(f"   Prompts salvos: {analytics_data.get('saved_prompts_count', 0)}")
            print(f"   Templates: {analytics_data.get('templates_count', 0)}")
        else:
            print(f"❌ Erro no analytics: {analytics_response.text}")
        
        # Prompts salvos (o que está com problema)
        print(f"\n4. 💾 Simulando carregamento dos prompts salvos...")
        saved_prompts_response = requests.get(f"{base_url}/api/members/saved-prompts", headers=headers)
        print(f"Saved prompts status: {saved_prompts_response.status_code}")
        
        if saved_prompts_response.status_code == 200:
            saved_data = saved_prompts_response.json()
            prompts = saved_data.get("prompts", [])
            total = saved_data.get("total", 0)
            
            print(f"✅ Prompts salvos carregados:")
            print(f"   Total no response: {total}")
            print(f"   Length do array: {len(prompts)}")
            
            if len(prompts) > 0:
                print(f"   📋 Primeiros prompts:")
                for i, prompt in enumerate(prompts[:3]):
                    title = prompt.get("title", "Sem título")
                    created = prompt.get("created_at", "N/A")
                    print(f"      {i+1}. {title} - {created}")
            else:
                print("   📭 Array de prompts está vazio!")
                
        else:
            print(f"❌ Erro nos prompts salvos: {saved_prompts_response.text}")
        
        print(f"\n" + "=" * 50)
        print("✅ Simulação completa!")
        
        # Resumo para área de membros
        if saved_prompts_response.status_code == 200:
            saved_data = saved_prompts_response.json()
            total = saved_data.get("total", 0)
            
            if total > 0:
                print(f"🎉 TUDO FUNCIONANDO! Usuário tem {total} prompts salvos")
                print(f"💡 Se ainda aparece 'Carregando...' em produção, é problema de:")
                print(f"   - Cache do navegador")
                print(f"   - Deploy não atualizado") 
                print(f"   - Problema de CORS/autenticação")
                print(f"   - Verificar console do navegador para erros")
            else:
                print(f"⚠️ API funcionando mas usuário não tem dados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante simulação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simulate_production_login()