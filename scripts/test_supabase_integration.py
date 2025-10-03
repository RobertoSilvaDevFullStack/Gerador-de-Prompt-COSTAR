#!/usr/bin/env python3
"""
Teste de integração completa do Supabase
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.supabase_auth_service import SupabaseAuthService
from app.services.member_area_service import MemberAreaService
from app.services.admin_analytics_service import AdminAnalyticsService
import asyncio

def test_supabase_integration():
    """Teste completo da integração Supabase"""
    print("🧪 TESTE DE INTEGRAÇÃO SUPABASE")
    print("="*40)
    
    # Inicializar serviços
    auth_service = SupabaseAuthService()
    member_service = MemberAreaService()
    analytics_service = AdminAnalyticsService()
    
    # Verificar conexão
    if not auth_service.enabled:
        print("❌ Supabase não configurado!")
        return False
    
    print("✅ Supabase conectado")
    
    # 1. Testar criação de usuário
    print("\n1. 👤 TESTANDO CRIAÇÃO DE USUÁRIO...")
    test_email = "test.user@gmail.com"
    test_password = "test123456"
    test_name = "Test User"
    
    # Limpar usuário de teste se existir
    existing_user = auth_service.get_user_by_email(test_email)
    if existing_user:
        print(f"   🗑️  Removendo usuário de teste existente: {test_email}")
        auth_service.delete_user(existing_user.id)
    
    # Criar usuário
    user = auth_service.register_user(test_email, test_password, test_name)
    if user:
        print(f"   ✅ Usuário criado: {user.email} (ID: {user.id})")
    else:
        print("   ❌ Falha ao criar usuário")
        return False
    
    # 2. Testar autenticação
    print("\n2. 🔐 TESTANDO AUTENTICAÇÃO...")
    token = auth_service.authenticate_user(test_email, test_password)
    if token:
        print(f"   ✅ Login bem-sucedido - Token: {token[:30]}...")
        
        # Verificar token
        user_from_token = auth_service.verify_token(token)
        if user_from_token:
            print(f"   ✅ Token válido para: {user_from_token.email}")
        else:
            print("   ❌ Token inválido")
            return False
    else:
        print("   ❌ Falha no login")
        return False
    
    # 3. Testar busca de usuários
    print("\n3. 🔍 TESTANDO BUSCA DE USUÁRIOS...")
    
    # Por ID
    user_by_id = auth_service.get_user_by_id(user.id)
    if user_by_id:
        print(f"   ✅ Busca por ID: {user_by_id.email}")
    else:
        print("   ❌ Falha na busca por ID")
        return False
    
    # Por email
    user_by_email = auth_service.get_user_by_email(test_email)
    if user_by_email:
        print(f"   ✅ Busca por email: {user_by_email.email}")
    else:
        print("   ❌ Falha na busca por email")
        return False
    
    # Todos os usuários
    all_users = auth_service.get_all_users()
    if all_users:
        print(f"   ✅ Lista de usuários: {len(all_users)} usuário(s)")
        for i, usr in enumerate(all_users[:3]):  # Mostrar apenas 3 primeiros
            print(f"      {i+1}. {usr.get('email', 'N/A')} ({usr.get('role', 'N/A')})")
    else:
        print("   ❌ Falha ao listar usuários")
        return False
    
    # 4. Testar integração com área de membros
    print("\n4. 🏠 TESTANDO ÁREA DE MEMBROS...")
    
    # Criar perfil de membro
    from app.services.member_area_service import SubscriptionPlan
    profile = member_service.get_member_profile(user.id)
    if not profile:
        profile = member_service.create_member_profile(
            user_id=user.id,
            username=user.username,
            email=user.email,
            subscription_plan=SubscriptionPlan.FREE
        )
        if profile:
            print(f"   ✅ Perfil de membro criado: {profile.username}")
        else:
            print("   ❌ Falha ao criar perfil de membro")
            return False
    else:
        print(f"   ✅ Perfil de membro existente: {profile.username}")
    
    # Verificar analytics
    analytics = member_service.get_member_analytics(user.id)
    if analytics:
        print(f"   ✅ Analytics do membro disponíveis")
    else:
        print("   ⚠️  Analytics não disponíveis (normal para usuário novo)")
    
    # 5. Testar criação de admin
    print("\n5. 👑 TESTANDO CRIAÇÃO DE ADMIN...")
    admin_email = "admin.test@gmail.com"
    admin_password = "admin123456"
    admin_name = "Test Admin"
    
    # Limpar admin de teste se existir
    existing_admin = auth_service.get_user_by_email(admin_email)
    if existing_admin:
        print(f"   🗑️  Removendo admin de teste existente: {admin_email}")
        auth_service.delete_user(existing_admin.id)
    
    # Criar admin
    admin = auth_service.create_admin_user(admin_email, admin_password, admin_name)
    if admin:
        print(f"   ✅ Admin criado: {admin.email} (Role: {admin.role.value})")
    else:
        print("   ❌ Falha ao criar admin")
        return False
    
    # 6. Testar analytics administrativos
    print("\n6. 📊 TESTANDO ANALYTICS ADMINISTRATIVOS...")
    try:
        dashboard_metrics = analytics_service.get_dashboard_metrics()
        if dashboard_metrics:
            print("   ✅ Métricas do dashboard obtidas:")
            print(f"      - Usuários totais: {dashboard_metrics.get('user_stats', {}).get('total_users', 0)}")
            print(f"      - Prompts gerados: {dashboard_metrics.get('usage_stats', {}).get('total_prompts', 0)}")
        else:
            print("   ⚠️  Métricas vazias (normal para ambiente novo)")
    except Exception as e:
        print(f"   ⚠️  Erro nas métricas: {str(e)}")
    
    # 7. Limpeza
    print("\n7. 🧹 LIMPEZA DE TESTE...")
    auth_service.delete_user(user.id)
    auth_service.delete_user(admin.id)
    print("   ✅ Usuários de teste removidos")
    
    print("\n🎉 TESTE DE INTEGRAÇÃO COMPLETO - SUCESSO!")
    return True

def test_real_data_flow():
    """Testar fluxo com dados reais"""
    print("\n" + "="*50)
    print("🔄 TESTE DE FLUXO COM DADOS REAIS")
    print("="*50)
    
    auth_service = SupabaseAuthService()
    
    # Listar usuários reais
    users = auth_service.get_all_users()
    print(f"📊 Total de usuários reais: {len(users)}")
    
    if users:
        print("\n👥 USUÁRIOS NO SISTEMA:")
        for i, user in enumerate(users, 1):
            email = user.get('email', 'N/A')
            role = user.get('role', 'N/A')
            is_active = user.get('is_active', False)
            status = "🟢 Ativo" if is_active else "🔴 Inativo"
            print(f"   {i}. {email} ({role}) - {status}")
    
    # Verificar se há pelo menos um admin
    admins = [u for u in users if u.get('role') == 'admin']
    if admins:
        print(f"\n👑 Administradores: {len(admins)}")
        for admin in admins:
            print(f"   - {admin.get('email', 'N/A')}")
    else:
        print("\n⚠️  NENHUM ADMINISTRADOR ENCONTRADO!")
        print("   Execute o script create_admin_user_supabase.py para criar um admin")
    
    return True

def main():
    """Função principal"""
    try:
        print("🚀 SISTEMA DE TESTES SUPABASE - COSTAR AI")
        print("="*50)
        
        # Teste de integração
        integration_ok = test_supabase_integration()
        
        if integration_ok:
            # Teste com dados reais
            test_real_data_flow()
            
            print("\n✅ TODOS OS TESTES PASSARAM!")
            print("📋 PRÓXIMOS PASSOS:")
            print("   1. Execute create_admin_user_supabase.py para criar admin")
            print("   2. Teste o dashboard administrativo")
            print("   3. Verifique a área de membros")
            
        else:
            print("\n❌ ALGUNS TESTES FALHARAM!")
            print("   Verifique as configurações do Supabase")
            
    except Exception as e:
        print(f"\n💥 ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()