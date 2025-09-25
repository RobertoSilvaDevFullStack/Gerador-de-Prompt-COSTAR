import requests
import json

def test_server():
    print("🚀 Testando o servidor COSTAR...")
    
    try:
        # Teste de health check
        print("\n1. 🔍 Testando Health Check...")
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   Status: {health_response.status_code}")
        print(f"   Response: {health_response.text}")
        
        # Teste de login
        print("\n2. 🔐 Testando Login...")
        login_data = {
            "email": "admin@costar.com",
            "password": "admin123"
        }
        
        login_response = requests.post(
            "http://localhost:8000/api/members/auth/login",
            json=login_data,
            timeout=5
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            result = login_response.json()
            print(f"   ✅ Login bem-sucedido!")
            print(f"   👤 Usuário: {result.get('user', {}).get('email', 'N/A')}")
            print(f"   🎭 Role: {result.get('user', {}).get('role', 'N/A')}")
            print(f"   🎫 Token: {result.get('access_token', 'N/A')[:50]}...")
            
            # Teste de rota protegida
            print("\n3. 🛡️ Testando Rota Protegida...")
            token = result.get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            me_response = requests.get(
                "http://localhost:8000/api/members/auth/me",
                headers=headers,
                timeout=5
            )
            
            print(f"   Status: {me_response.status_code}")
            if me_response.status_code == 200:
                user_info = me_response.json()
                print(f"   ✅ Autenticação válida!")
                print(f"   👤 Dados: {json.dumps(user_info, indent=2)}")
            else:
                print(f"   ❌ Erro na autenticação: {me_response.text}")
        else:
            print(f"   ❌ Erro no login: {login_response.text}")
            
        # Teste de página principal
        print("\n4. 🌐 Testando Página Principal...")
        index_response = requests.get("http://localhost:8000/", timeout=5)
        print(f"   Status: {index_response.status_code}")
        if index_response.status_code == 200:
            print(f"   ✅ Página principal carregou!")
            print(f"   📄 Tamanho: {len(index_response.text)} bytes")
        else:
            print(f"   ❌ Erro na página: {index_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor. Verifique se está rodando na porta 8000.")
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout ao conectar com o servidor.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_server()