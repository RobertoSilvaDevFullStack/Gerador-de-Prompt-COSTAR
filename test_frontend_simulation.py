#!/usr/bin/env python3
"""
Teste final - simula o frontend carregando dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.member_area_service import MemberAreaService

def simulate_frontend_loading():
    """Simula o carregamento de dados que o frontend faz"""
    
    print("🎯 Simulando carregamento da área de membros...")
    
    service = MemberAreaService()
    user_id = "34a26484-f48f-4a1c-a1a6-0eaeca401d5e"
    
    print(f"\n👤 User ID: {user_id}")
    
    # 1. Analytics (funciona)
    print("\n📊 1. Carregando Analytics...")
    analytics = service.get_member_analytics(user_id)
    print(f"✅ Analytics carregadas:")
    print(f"   - Total prompts: {analytics.total_prompts_generated}")
    print(f"   - Prompts este mês: {analytics.prompts_this_month}")
    print(f"   - Prompts salvos: {analytics.saved_templates_count}")
    print(f"   - Membro desde: {analytics.member_since}")
    
    # 2. Quota (agora corrigida)
    print("\n💾 2. Carregando Quotas...")
    quota = service.check_monthly_quota(user_id)
    print(f"✅ Quotas carregadas:")
    print(f"   - Usado: {quota.get('used')}")
    print(f"   - Limite: {quota.get('limit')}")
    print(f"   - Permitido: {quota.get('allowed')}")
    print(f"   - Restante: {quota.get('remaining')}")
    if quota.get('reason'):
        print(f"   - Razão: {quota.get('reason')}")
    
    # 3. Prompts Salvos (vazio mas funciona)
    print("\n💾 3. Carregando Prompts Salvos...")
    saved_prompts = service.get_user_saved_prompts(user_id)
    print(f"✅ Prompts salvos: {len(saved_prompts)} prompts")
    
    # 4. Templates
    print("\n📄 4. Carregando Templates...")
    templates = service.get_user_templates(user_id)
    print(f"✅ Templates: {len(templates)} templates")
    
    # 5. Perfil
    print("\n👤 5. Carregando Perfil...")
    profile = service.get_member_profile(user_id)
    if profile:
        print(f"✅ Perfil carregado:")
        print(f"   - Username: {profile.username}")
        print(f"   - Email: {profile.email}")
        print(f"   - Plano: {profile.subscription_plan}")
        print(f"   - Criado em: {profile.created_at}")
    
    print("\n🎉 Todos os dados foram carregados com sucesso!")
    print("📝 O problema da área de membros parece estar resolvido.")

if __name__ == "__main__":
    simulate_frontend_loading()