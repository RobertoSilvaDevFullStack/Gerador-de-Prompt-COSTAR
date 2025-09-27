#!/usr/bin/env python3
"""
Teste específico dos endpoints de membros após correção
"""
import requests
import json
import time

def test_member_endpoints():
    print("👥 TESTANDO ENDPOINTS DE MEMBROS APÓS CORREÇÃO")
    print("="*55)
    
    base_url = "http://localhost:8000"
    
    # Aguarda servidor estar pronto
    time.sleep(2)
    
    # Primeiro faz login para obter token
    login_data = {
        "email": "admin@costar.com",
        "password": "admin123"
    }
    
    try:
        print("1. Fazendo login...")
        login_response = requests.post(f"{base_url}/api/members/auth/login", 
                                     json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            
            login_data = login_response.json()
            token = login_data.get('access_token')
            
            if token:
                print("   ✅ Token obtido")
                
                # Headers com autenticação
                headers = {"Authorization": f"Bearer {token}"}
                
                # Testa endpoint que estava dando erro de username
                print("\\n2. Testando perfil de membro (endpoint que tinha erro)...")
                profile_response = requests.get(f"{base_url}/api/members/profile", 
                                              headers=headers, timeout=10)
                
                print(f"   Status: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    print("   ✅ Endpoint de perfil funcionando!")
                    profile_data = profile_response.json()
                    print(f"   📊 Profile keys: {list(profile_data.keys())}")
                elif profile_response.status_code == 500:
                    print("   ❌ Ainda há erro interno no servidor")
                    try:
                        error_data = profile_response.json()
                        print(f"   🔍 Erro: {error_data}")
                    except:
                        print("   🔍 Não foi possível obter detalhes do erro")
                else:
                    print(f"   ⚠️  Status inesperado: {profile_response.status_code}")
                    
            else:
                print("   ❌ Token não encontrado na resposta")
        else:
            print(f"   ❌ Falha no login: {login_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está acessível")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
    
    print("\\n" + "="*55)
    print("🎯 TESTE DE ENDPOINTS DE MEMBROS CONCLUÍDO!")

if __name__ == "__main__":
    test_member_endpoints()