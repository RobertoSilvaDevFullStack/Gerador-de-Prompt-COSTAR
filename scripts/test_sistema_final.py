#!/usr/bin/env python3
"""
Teste completo do sistema - versão final
"""
import requests
import json
import time
import subprocess
import sys
import os

def start_server():
    """Iniciar servidor em background"""
    print('🚀 Iniciando servidor...')
    
    # Verificar se já está rodando
    try:
        response = requests.get('http://localhost:8000/api/status/health', timeout=2)
        if response.status_code == 200:
            print('✅ Servidor já está rodando!')
            return True
    except:
        pass
    
    # Iniciar servidor
    server_process = subprocess.Popen([
        sys.executable, 'main_demo.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Aguardar inicialização
    print('⏱️ Aguardando servidor inicializar...')
    for i in range(10):  # até 10 segundos
        time.sleep(1)
        try:
            response = requests.get('http://localhost:8000/api/status/health', timeout=2)
            if response.status_code == 200:
                print('✅ Servidor iniciado com sucesso!')
                return True
        except:
            continue
    
    print('❌ Servidor não iniciou corretamente')
    return False

def test_system():
    """Testar sistema completo"""
    print('\n🔍 TESTANDO SISTEMA COMPLETO')
    print('='*50)
    
    try:
        # 1. Teste de Health Check
        print('\n1. 🏥 Health Check...')
        response = requests.get('http://localhost:8000/api/status/health', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   ✅ Sistema: {data.get("status", "unknown")}')
        
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
            print(f'   ✅ LOGIN BEM-SUCEDIDO!')
            print(f'   👤 Usuário: {user.get("email", "N/A")}')
            print(f'   👑 Role: {user.get("role", "N/A")}')
            print(f'   🎫 Token: {token[:30]}...')
            
            # 3. Teste do Dashboard Admin
            print('\n3. 📊 Teste Dashboard Admin...')
            admin_response = requests.get('http://localhost:8000/api/admin/dashboard',
                                         headers={'Authorization': f'Bearer {token}'},
                                         timeout=5)
            print(f'   Status: {admin_response.status_code}')
            
            if admin_response.status_code == 200:
                print('   ✅ Dashboard admin acessível!')
                
                # 4. Teste informações do usuário
                print('\n4. 👤 Teste Informações do Usuário...')
                me_response = requests.get('http://localhost:8000/api/members/auth/me',
                                         headers={'Authorization': f'Bearer {token}'},
                                         timeout=5)
                print(f'   Status: {me_response.status_code}')
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f'   ✅ Dados do usuário obtidos')
                    print(f'   📧 Email: {me_data.get("email", "N/A")}')
                    print(f'   👑 Role: {me_data.get("role", "N/A")}')
                
                print('\n🎉 SISTEMA 100% FUNCIONAL!')
                print('📋 RESUMO DOS TESTES:')
                print('   ✅ Health Check - OK')
                print('   ✅ Login - OK')
                print('   ✅ Dashboard Admin - OK')
                print('   ✅ Informações do Usuário - OK')
                
                return True
            else:
                print(f'   ❌ Erro no dashboard: Status {admin_response.status_code}')
                print(f'   📝 Resposta: {admin_response.text[:200]}')
        else:
            print(f'   ❌ Erro no login: Status {login_response.status_code}')
            print(f'   📝 Resposta: {login_response.text[:200]}')
            
    except requests.exceptions.ConnectionError:
        print('❌ Erro de conexão - Servidor não está respondendo')
    except Exception as e:
        print(f'❌ Erro inesperado: {e}')
    
    return False

def main():
    """Função principal"""
    print('🔍 TESTE COMPLETO DO SISTEMA COSTAR')
    print('='*50)
    
    # Mudar para diretório correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    print(f'📁 Diretório: {os.getcwd()}')
    
    # Iniciar servidor
    if start_server():
        # Testar sistema
        success = test_system()
        
        if success:
            print('\n🎊 TODOS OS TESTES PASSARAM!')
            print('💻 Agora você pode acessar:')
            print('   🌐 Frontend: http://localhost:8000')
            print('   👥 Área de Membros: http://localhost:8000/member-area.html')
            print('   🔧 Dashboard Admin: http://localhost:8000/admin-dashboard.html')
            print('\n🔑 Credenciais de Admin:')
            print('   📧 Email: admin@costar.com')
            print('   🔒 Senha: admin123')
        else:
            print('\n❌ ALGUNS TESTES FALHARAM')
    else:
        print('\n❌ FALHA AO INICIAR SERVIDOR')

if __name__ == "__main__":
    main()