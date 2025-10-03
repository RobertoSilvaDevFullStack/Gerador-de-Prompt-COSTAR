#!/usr/bin/env python3
"""
Script para debugar problema específico de quota
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.member_area_service import MemberAreaService

def debug_quota_function():
    """Debug específico da função de quota"""
    
    print("🔍 Debugando função check_monthly_quota...")
    
    service = MemberAreaService()
    user_id = "34a26484-f48f-4a1c-a1a6-0eaeca401d5e"  # ID do admin
    
    try:
        print(f"\n1. Testando get_member_profile para user_id: {user_id}")
        profile = service.get_member_profile(user_id)
        
        if profile:
            print(f"   ✅ Perfil encontrado:")
            print(f"       - user_id: {profile.user_id}")
            print(f"       - subscription_plan: {profile.subscription_plan}")
            print(f"       - usage_current_month: {profile.usage_current_month}")
        else:
            print(f"   ❌ Perfil não encontrado!")
            return
        
        print(f"\n2. Verificando plan_quotas para plano '{profile.subscription_plan}'")
        try:
            plan_limits = service.plan_quotas[profile.subscription_plan]
            print(f"   ✅ Plan limits: {plan_limits}")
            
            monthly_limit = plan_limits['monthly_prompts']
            print(f"   ✅ Monthly limit: {monthly_limit}")
        except Exception as e:
            print(f"   ❌ Erro ao acessar plan_quotas: {e}")
            return
        
        print(f"\n3. Testando check_monthly_quota completa...")
        quota_result = service.check_monthly_quota(user_id)
        print(f"   Resultado: {quota_result}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_quota_function()