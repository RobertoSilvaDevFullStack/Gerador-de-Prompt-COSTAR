#!/usr/bin/env python3
"""
Teste direto das funções sem servidor HTTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.member_area_service import MemberAreaService

def test_quota_directly():
    """Teste direto da quota sem API"""
    
    print("🔬 Testando função de quota diretamente...")
    
    service = MemberAreaService()
    user_id = "34a26484-f48f-4a1c-a1a6-0eaeca401d5e"
    
    # Teste direto
    print("\n1. Testando check_monthly_quota diretamente...")
    result = service.check_monthly_quota(user_id)
    print(f"Resultado: {result}")
    
    # Teste get_member_profile
    print("\n2. Testando get_member_profile...")
    profile = service.get_member_profile(user_id)
    if profile:
        print(f"✅ Perfil encontrado: {profile.user_id}")
        print(f"   Plan: {profile.subscription_plan} (tipo: {type(profile.subscription_plan)})")
        
        # Verificar se é enum
        if hasattr(profile.subscription_plan, 'value'):
            print(f"   Plan value: {profile.subscription_plan.value}")
        
        print(f"   Usage: {profile.usage_current_month}")
    else:
        print("❌ Perfil não encontrado")
    
    # Teste plan_quotas
    print(f"\n3. Plan quotas disponíveis:")
    for key, value in service.plan_quotas.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    test_quota_directly()