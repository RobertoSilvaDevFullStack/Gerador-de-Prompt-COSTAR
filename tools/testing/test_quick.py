import requests
import time

print("🌐 TESTE RÁPIDO DO FRONTEND")
print("="*30)

# Aguarda um pouco
time.sleep(2)

try:
    # Teste 1: Health check
    response = requests.get("http://localhost:8000/api/status/health", timeout=5)
    print(f"Health Check: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Mode: {data.get('mode', 'unknown')}")
    
    # Teste 2: Página principal
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f"Frontend: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if response.status_code == 200:
        has_costar = 'COSTAR' in response.text
        print(f"  COSTAR content: {'✅' if has_costar else '❌'}")
    
    print("\n✅ Testes básicos concluídos!")
    
except requests.exceptions.ConnectionError:
    print("❌ Servidor não está acessível")
except Exception as e:
    print(f"❌ Erro: {e}")