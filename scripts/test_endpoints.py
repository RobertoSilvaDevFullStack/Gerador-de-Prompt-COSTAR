#!/usr/bin/env python3
"""
Script para testar os endpoints de status
"""
import requests
import json
import time

def test_endpoints():
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/status/health",
        "/api/status/database", 
        "/api/status/features"
    ]
    
    print("🔍 Testando endpoints de status...")
    print("📍 Certifique-se de que o servidor está rodando: python main_demo.py")
    print()
    
    for endpoint in endpoints:
        try:
            print(f"🔗 Testando {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                # Mostra informações específicas de cada endpoint
                if "health" in endpoint:
                    print(f"   📊 Mode: {data.get('backend', {}).get('mode', 'unknown')}")
                    print(f"   🔌 Connected: {data.get('backend', {}).get('connected', False)}")
                
                elif "database" in endpoint:
                    print(f"   💾 Mode: {data.get('mode', 'unknown')}")
                    print(f"   📊 Status: {data.get('status', 'unknown')}")
                
                elif "features" in endpoint:
                    ai_info = data.get('ai_providers', {})
                    print(f"   🤖 AI Providers: {ai_info.get('total_configured', 0)}")
                    print(f"   🔄 Multi-AI: {ai_info.get('multi_ai_enabled', False)}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Conexão recusada - servidor não está rodando")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
    
    print("✅ Teste de endpoints concluído!")

if __name__ == "__main__":
    test_endpoints()