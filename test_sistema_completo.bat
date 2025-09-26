@echo off
REM Script para testar o sistema com servidor em background

echo 🚀 Iniciando servidor em background...
start /B cmd /c "python main_demo.py > server_output.log 2>&1"

echo ⏱️ Aguardando servidor inicializar...
timeout /T 3 /NOBREAK > nul

echo 🔍 Testando endpoints...
python -c "
import requests
import json
import time

def test_with_retries():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Teste básico de health
            response = requests.get('http://localhost:8000/api/status/health', timeout=5)
            print(f'✅ Health Status: {response.status_code}')
            
            # Teste de login
            login_data = {'email': 'admin@costar.com', 'password': 'admin123'}
            login_response = requests.post('http://localhost:8000/api/members/auth/login', 
                                         json=login_data, 
                                         headers={'Content-Type': 'application/json'},
                                         timeout=5)
            
            print(f'🔐 Login Status: {login_response.status_code}')
            
            if login_response.status_code == 200:
                result = login_response.json()
                token = result.get('access_token', '')
                user = result.get('user', {})
                print(f'✅ LOGIN BEM-SUCEDIDO!')
                print(f'👤 Usuário: {user.get(\"email\")}')
                print(f'👑 Role: {user.get(\"role\")}')
                
                # Teste do dashboard admin
                admin_response = requests.get('http://localhost:8000/api/admin/dashboard',
                                             headers={'Authorization': f'Bearer {token}'},
                                             timeout=5)
                print(f'📊 Dashboard Status: {admin_response.status_code}')
                
                if admin_response.status_code == 200:
                    print('✅ Dashboard admin acessível!')
                    print('🎉 SISTEMA 100%% FUNCIONAL!')
                else:
                    print(f'❌ Erro no dashboard: Status {admin_response.status_code}')
            else:
                print(f'❌ Erro no login: {login_response.text[:100]}')
            
            break
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f'⏳ Tentativa {attempt + 1}/{max_retries} - Aguardando servidor...')
                time.sleep(2)
            else:
                print('❌ Servidor não está respondendo')
        except Exception as e:
            print(f'❌ Erro: {e}')
            break

test_with_retries()
"

echo.
echo 🛑 Parando servidor...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq main_demo.py*" 2>nul
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq main_demo.py*" 2>nul

echo ✅ Teste concluído!
pause