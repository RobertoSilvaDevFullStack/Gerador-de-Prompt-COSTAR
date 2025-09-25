#!/usr/bin/env python3
"""
Script para simular dados no dashboard e testar as correções
"""
import json
import os
from datetime import datetime, timedelta

def create_sample_data():
    """Criar dados de exemplo para testar o dashboard"""
    
    # Dados para API usage logs
    api_logs = []
    user_activities = []
    
    # Gerar logs dos últimos 7 dias
    base_date = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        
        # API calls para este dia
        calls_count = 10 + (day * 5)  # Crescimento gradual
        
        for call in range(calls_count):
            api_logs.append({
                "id": f"log_{day}_{call}",
                "provider": ["groq", "gemini", "huggingface", "cohere", "together"][call % 5],
                "user_id": f"user_{(call % 10) + 1}",
                "prompt_type": "costar",
                "request_time": (current_date + timedelta(hours=call % 24)).isoformat(),
                "response_time": 0.5 + (call * 0.1),
                "success": call % 10 != 9,  # 90% success rate
                "error_message": "Rate limit exceeded" if call % 10 == 9 else None,
                "tokens_used": 100 + (call * 10),
                "ip_address": "127.0.0.1",
                "user_agent": "test-agent"
            })
        
        # User activities para este dia
        for user in range(5):
            user_activities.append({
                "id": f"activity_{day}_{user}",
                "user_id": f"user_{user + 1}",
                "action": "generate_prompt",
                "timestamp": (current_date + timedelta(hours=user * 2)).isoformat(),
                "details": {"prompt_type": "costar", "tokens": 150},
                "ip_address": "127.0.0.1",
                "user_agent": "test-agent"
            })
    
    # Salvar dados
    os.makedirs('data', exist_ok=True)
    
    with open('data/api_usage_logs.json', 'w') as f:
        json.dump(api_logs, f, indent=2)
    
    with open('data/user_activities.json', 'w') as f:
        json.dump(user_activities, f, indent=2)
    
    print(f"✅ Criados {len(api_logs)} logs de API")
    print(f"✅ Criadas {len(user_activities)} atividades de usuário")
    print("✅ Dados de exemplo salvos em data/")

def test_analytics_service():
    """Testar o serviço de analytics com os dados criados"""
    import sys
    sys.path.append('.')
    
    from services.admin_analytics_service import AdminAnalyticsService
    
    analytics = AdminAnalyticsService()
    metrics = analytics.get_dashboard_metrics()
    
    print("\n📊 Métricas calculadas:")
    print(f"Total API calls: {metrics['overview']['total_api_calls']}")
    print(f"API calls 24h: {metrics['overview']['api_calls_24h']}")
    print(f"Active users 24h: {metrics['overview']['active_users_24h']}")
    print(f"Error rate 24h: {metrics['overview']['error_rate_24h']:.1f}%")
    
    # Verificar dados dos gráficos
    charts_data = metrics.get('charts_data', {})
    timeline = charts_data.get('timeline', {})
    
    print(f"\n📈 Timeline data:")
    print(f"Dates: {len(timeline.get('dates', []))} days")
    print(f"API calls: {timeline.get('api_calls', [])}")
    print(f"Active users: {timeline.get('active_users', [])}")
    
    provider_dist = charts_data.get('provider_distribution', {})
    print(f"\n🔄 Provider distribution:")
    print(f"Labels: {provider_dist.get('labels', [])}")
    print(f"Data: {provider_dist.get('data', [])}")
    
    return metrics

def main():
    """Função principal"""
    print("🚀 Criando dados de exemplo para o dashboard\n")
    
    # Criar dados de exemplo
    create_sample_data()
    
    # Testar o serviço
    print("\n🔍 Testando AdminAnalyticsService...")
    metrics = test_analytics_service()
    
    print("\n✅ Dados criados com sucesso!")
    print("\n📋 Para testar o dashboard:")
    print("1. Inicie o servidor: python main.py")
    print("2. Acesse: http://localhost:8000/frontend/admin-dashboard.html")
    print("3. Faça login como admin@costar.com / admin123")
    print("4. Verifique se os gráficos carregam corretamente")

if __name__ == "__main__":
    main()