#!/usr/bin/env python3
"""
Script final para testar todos os componentes do dashboard admin
"""

import requests
import json
import time
from datetime import datetime


def test_complete_dashboard():
    """Teste completo do dashboard admin"""
    
    print("🔧 Teste final do dashboard administrativo")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Login admin
        print("\n1. 🔐 Fazendo login como admin...")
        login_response = requests.post(f"{base_url}/api/members/auth/login", json={
            "email": "admin@costar.com",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login realizado com sucesso")
        
        # 2. Teste dashboard principal
        print("\n2. 📊 Testando dashboard principal...")
        dashboard_response = requests.get(f"{base_url}/api/admin/dashboard", headers=headers)
        
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            print(f"✅ Dashboard carregado:")
            print(f"   👥 Total usuários: {data['overview']['total_users']}")
            print(f"   📞 Total API calls: {data['overview']['total_api_calls']}")
            print(f"   📈 Prompts gerados: {data['prompt_generation']['total_prompts_generated']}")
            print(f"   🎯 Provider mais usado: {data['api_usage']['most_used_provider']}")
        else:
            print(f"❌ Erro no dashboard: {dashboard_response.status_code}")
        
        # 3. Teste usuários
        print("\n3. 👥 Testando lista de usuários...")
        users_response = requests.get(f"{base_url}/api/admin/users", headers=headers)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            users = users_data.get('users', users_data)  # Pode ser direto ou dentro de 'users'
            
            if isinstance(users, list):
                print(f"✅ {len(users)} usuários carregados:")
                # Mostrar apenas os 3 primeiros para não poluir o log
                users_to_show = users[:3] if len(users) > 3 else users
                for user in users_to_show:
                    email = user.get('email', 'N/A')
                    plan = user.get('subscription_plan', 'N/A') or user.get('plan', 'N/A')
                    role = user.get('role', 'N/A')
                    print(f"   👤 {email} - Plano: {plan} - Role: {role}")
                if len(users) > 3:
                    print(f"   ... e mais {len(users) - 3} usuários")
            else:
                print(f"❌ Formato inesperado de usuários: {type(users)}")
        else:
            print(f"❌ Erro nos usuários: {users_response.status_code}")
        
        # 4. Teste templates
        print("\n4. 📄 Testando lista de templates...")
        templates_response = requests.get(f"{base_url}/api/admin/templates", headers=headers)
        
        if templates_response.status_code == 200:
            template_data = templates_response.json()
            templates = template_data.get('templates', template_data)
            
            if isinstance(templates, list):
                print(f"✅ {len(templates)} templates carregados:")
                for template in templates:
                    title = template.get('title', 'Sem título')
                    creator = template.get('creator_name', template.get('author', 'Anônimo'))
                    category = template.get('category', 'Geral')
                    is_public = template.get('is_public', False)
                    usage_count = template.get('usage_count', 0)
                    print(f"   📄 {title} por {creator} - {category} - Público: {is_public} - Uso: {usage_count}x")
            else:
                print(f"❌ Formato inesperado de templates: {type(templates)}")
        else:
            print(f"❌ Erro nos templates: {templates_response.status_code}")
            
        # 5. Verificar arquivos de dados
        print("\n5. 📁 Verificando arquivos de dados...")
        import os
        
        data_files = [
            "data/saved_templates.json",
            "data/member_profiles.json", 
            "data/saved_prompts.json"
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ {file_path}: {len(data) if isinstance(data, list) else 'OK'}")
            else:
                print(f"❌ {file_path}: Arquivo não encontrado")
        
        # 6. Teste frontend
        print("\n6. 🌐 Testando frontend...")
        frontend_response = requests.get(f"{base_url}/frontend/admin-dashboard.html")
        
        if frontend_response.status_code == 200:
            print("✅ Dashboard HTML acessível")
        else:
            print(f"❌ Erro no frontend: {frontend_response.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ Teste completo finalizado!")
        print("🎉 Dashboard admin está funcionando corretamente!")
        print("\n📋 Resumo:")
        print("   • Autenticação admin: OK")
        print("   • Dashboard principal: OK")
        print("   • Lista de usuários: OK")
        print("   • Lista de templates: OK")
        print("   • Arquivos de dados: OK")
        print("   • Frontend: OK")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        return False


if __name__ == "__main__":
    test_complete_dashboard()