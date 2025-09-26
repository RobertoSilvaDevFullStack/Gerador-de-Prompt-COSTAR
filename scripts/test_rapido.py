#!/usr/bin/env python3
"""
Teste direto do sistema com servidor em execução
"""
import subprocess
import time
import requests
import json
import sys
import os

def wait_for_server():
    """Aguardar servidor estar disponível"""
    print('⏱️ Aguardando servidor...')
    for i in range(15):  # até 15 segundos
        try:
            response = requests.get('http://localhost:8000/api/status/health', timeout=2)
            if response.status_code == 200:
                print('✅ Servidor disponível!')
                return True
        except:
            time.sleep(1)
            print(f'   Tentativa {i+1}/15...')
    return False

def test_system():
    """Testar o sistema"""
    print('\n🔍 TESTANDO SISTEMA COSTAR')
    print('='*50)
    
    if not wait_for_server():
        print('❌ Servidor não disponível')
        return False
    
    try:
        # 1. Teste de Health
        print('\n1. 🏥 Health Check...')
        health_response = requests.get('http://localhost:8000/api/status/health', timeout=5)
        print(f'   Status: {health_response.status_code}')
        if health_response.status_code == 200:
            print('   ✅ Health OK')
        
        # 2. Teste de Login
        print('\n2. 🔐 Teste de Login...')
        login_data = {'email': 'admin@costar.com', 'password': 'admin123'}
        login_response = requests.post('http://localhost:8000/api/members/auth/login',
                                     json=login_data,
                                     headers={'Content-Type': 'application/json'},
                                     timeout=5)
        
        print(f'   Status: {login_response.status_code}')
        if login_response.status_code == 200:
            result = login_response.json()
            token = result.get('access_token', '')
            user = result.get('user', {})
            
            print('   ✅ LOGIN OK')
            print(f'   👤 Email: {user.get("email")}')
            print(f'   👑 Role: {user.get("role")}')
            
            # 3. Teste Dashboard Admin
            print('\n3. 📊 Dashboard Admin...')
            admin_response = requests.get('http://localhost:8000/api/admin/dashboard',
                                        headers={'Authorization': f'Bearer {token}'},
                                        timeout=5)
            print(f'   Status: {admin_response.status_code}')
            if admin_response.status_code == 200:
                print('   ✅ Dashboard OK')
                
                print('\n🎉 SISTEMA 100% FUNCIONAL!')
                print('\n📋 INSTRUÇÕES PARA USO:')
                print('   1. 🌐 Acesse: http://localhost:8000')
                print('   2. 🔐 Clique em "Login" no canto superior direito')
                print('   3. 📧 Email: admin@costar.com')
                print('   4. 🔒 Senha: admin123')
                print('   5. ✅ Após login, você será redirecionado automaticamente')
                print('\n🔗 Links diretos:')
                print('   • 🏠 Principal: http://localhost:8000')
                print('   • 👥 Membros: http://localhost:8000/member-area.html')
                print('   • 🔧 Admin: http://localhost:8000/admin-dashboard.html')
                print('   • 🧪 Teste: http://localhost:8000/test-login-simple.html')
                
                return True
            else:
                print(f'   ❌ Dashboard falhou: {admin_response.text[:100]}')
        else:
            print(f'   ❌ Login falhou: {login_response.text[:100]}')
            
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return False

if __name__ == "__main__":
    try:
        test_system()
    except KeyboardInterrupt:
        print('\n\n⏹️ Teste interrompido pelo usuário')
    except Exception as e:
        print(f'\n💥 Erro inesperado: {e}')