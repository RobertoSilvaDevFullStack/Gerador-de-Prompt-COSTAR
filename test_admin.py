import requests
import json

def test_admin_dashboard():
    print("🔧 Testando Admin Dashboard...")
    
    try:
        # 1. Login como admin
        print("\n1. 🔐 Fazendo login como admin...")
        login_data = {
            "email": "admin@costar.com",
            "password": "admin123"
        }
        
        login_response = requests.post(
            "http://localhost:8000/api/members/auth/login",
            json=login_data,
            timeout=5
        )
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
            
        result = login_response.json()
        token = result.get('access_token')
        user = result.get('user', {})
        
        print(f"✅ Login bem-sucedido!")
        print(f"👤 Email: {user.get('email')}")
        print(f"🎭 Role: {user.get('role')}")
        
        # 2. Testar rota admin dashboard
        print("\n2. 📊 Testando rota admin dashboard...")
        headers = {"Authorization": f"Bearer {token}"}
        
        dashboard_response = requests.get(
            "http://localhost:8000/api/admin/dashboard",
            headers=headers,
            timeout=5
        )
        
        print(f"Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ Admin dashboard funcionando!")
            print(f"📈 Dados obtidos: {len(dashboard_data)} chaves")
            
            # Mostrar estrutura dos dados
            for key, value in dashboard_data.items():
                if isinstance(value, dict):
                    print(f"  {key}: {len(value)} itens")
                elif isinstance(value, list):
                    print(f"  {key}: {len(value)} elementos")
                else:
                    print(f"  {key}: {value}")
                    
        elif dashboard_response.status_code == 403:
            print(f"❌ Acesso negado: {dashboard_response.text}")
        else:
            print(f"❌ Erro: {dashboard_response.status_code} - {dashboard_response.text}")
            
        # 3. Testar outras rotas admin
        print("\n3. 👥 Testando rota de usuários...")
        users_response = requests.get(
            "http://localhost:8000/api/admin/users",
            headers=headers,
            timeout=5
        )
        
        print(f"Status usuários: {users_response.status_code}")
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"✅ {len(users_data)} usuários encontrados")
        else:
            print(f"❌ Erro usuários: {users_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando na porta 8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_admin_dashboard()