#!/usr/bin/env python3
"""
Script para mostrar resumo completo dos dados criados para o admin
"""

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.member_area_service import MemberAreaService
from services.supabase_auth_service import SupabaseAuthService

def show_created_data_summary():
    """Mostrar resumo de todos os dados criados"""
    print("📊 RESUMO COMPLETO DOS DADOS CRIADOS")
    print("=" * 60)
    
    auth_service = SupabaseAuthService()
    member_service = MemberAreaService()
    
    # 1. Usuários criados
    print("\n👥 USUÁRIOS CRIADOS:")
    test_emails = [
        "joao.silva@email.com",
        "maria.santos@email.com", 
        "pedro.oliveira@email.com",
        "ana.costa@email.com",
        "carlos.ferreira@email.com"
    ]
    
    for email in test_emails:
        user = auth_service.get_user_by_email(email)
        if user:
            print(f"   ✅ {email} (ID: {user.id[:8]}..., Role: {user.role.value})")
        else:
            print(f"   ❌ {email} (não encontrado)")
    
    # 2. Perfis de membros
    print(f"\n👤 PERFIS DE MEMBROS:")
    profiles_count = 0
    try:
        with open('data/member_profiles.json', 'r', encoding='utf-8') as f:
            profiles = json.load(f)
            profiles_count = len(profiles)
            
        for profile in profiles[-5:]:  # Últimos 5 perfis
            print(f"   ✅ {profile['username']} ({profile['subscription_plan']}) - Criado: {profile['created_at'][:10]}")
            
    except Exception as e:
        print(f"   ❌ Erro ao carregar perfis: {e}")
    
    # 3. Templates públicos
    print(f"\n📄 TEMPLATES PÚBLICOS:")
    templates_count = 0
    try:
        with open('data/saved_templates.json', 'r', encoding='utf-8') as f:
            templates = json.load(f)
            templates_count = len(templates)
            
        for template in templates[-5:]:  # Últimos 5 templates
            print(f"   ✅ {template['title']} (por {template['creator_name']}) - Categoria: {template['category']}")
            
    except Exception as e:
        print(f"   ❌ Erro ao carregar templates: {e}")
    
    # 4. Prompts salvos
    print(f"\n💾 PROMPTS SALVOS:")
    prompts_count = 0
    try:
        with open('data/saved_prompts.json', 'r', encoding='utf-8') as f:
            prompts = json.load(f)
            prompts_count = len(prompts)
            
        # Agrupar por usuário
        user_prompts = {}
        for prompt in prompts:
            user_id = prompt.get('user_id', 'unknown')
            if user_id not in user_prompts:
                user_prompts[user_id] = []
            user_prompts[user_id].append(prompt)
        
        for user_id, user_prompt_list in user_prompts.items():
            # Buscar nome do usuário
            user_name = "Usuário Desconhecido"
            for profile in profiles:
                if profile['user_id'] == user_id:
                    user_name = profile['username']
                    break
            
            print(f"   👤 {user_name}: {len(user_prompt_list)} prompts")
            for prompt in user_prompt_list[:2]:  # Primeiros 2 prompts
                print(f"      • {prompt['title']} ({prompt['style']})")
            
    except Exception as e:
        print(f"   ❌ Erro ao carregar prompts: {e}")
    
    # 5. Estatísticas finais
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   👥 Total de usuários: {len(test_emails)} usuários de teste + 1 admin")
    print(f"   👤 Total de perfis: {profiles_count}")
    print(f"   📄 Total de templates: {templates_count}")
    print(f"   💾 Total de prompts: {prompts_count}")
    
    # 6. Dados de analytics simulados
    print(f"\n🎯 DADOS PARA DASHBOARD ADMIN:")
    print(f"   📈 Usuários ativos: {profiles_count} usuários")
    print(f"   📊 Prompts gerados: {prompts_count} prompts")
    print(f"   📋 Templates disponíveis: {templates_count} templates")
    print(f"   🔧 Funcionalidades: Gestão completa de usuários, quotas e conteúdo")
    
    # 7. Instruções para teste
    print(f"\n🔑 COMO TESTAR:")
    print(f"   1. Acesse: http://localhost:8000/frontend/admin-dashboard.html")
    print(f"   2. Login admin: admin@costar.com / admin123")
    print(f"   3. Veja os dados: usuários, métricas, templates, prompts")
    print(f"   4. Teste gestão: editar perfis, quotas, aprovar conteúdo")
    
    print(f"\n🎉 SISTEMA PRONTO PARA DEMONSTRAÇÃO!")
    print("=" * 60)

if __name__ == "__main__":
    show_created_data_summary()