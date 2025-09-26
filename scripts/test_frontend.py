#!/usr/bin/env python3
"""
Teste completo do frontend
"""
import requests
import json
import time

def test_frontend():
    print("🌐 TESTE COMPLETO DO FRONTEND")
    print("="*50)
    
    base_url = "http://localhost:8000"
    
    tests = [
        {
            "name": "Health Check",
            "endpoint": "/api/status/health",
            "method": "GET"
        },
        {
            "name": "Database Status", 
            "endpoint": "/api/status/database",
            "method": "GET"
        },
        {
            "name": "Features Status",
            "endpoint": "/api/status/features", 
            "method": "GET"
        },
        {
            "name": "Página Principal",
            "endpoint": "/",
            "method": "GET"
        },
        {
            "name": "Generate Prompt",
            "endpoint": "/api/generate-prompt",
            "method": "POST",
            "data": {
                "contexto": "Sistema de geração de prompts",
                "objetivo": "Criar um prompt eficaz",
                "estilo": "Técnico e claro",
                "tom": "Profissional",
                "audiencia": "Desenvolvedores",
                "resposta": "Lista estruturada"
            }
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🔍 Testando: {test['name']}")
        try:
            url = base_url + test['endpoint']
            
            if test['method'] == 'GET':
                response = requests.get(url, timeout=10)
            elif test['method'] == 'POST':
                response = requests.post(url, json=test.get('data'), timeout=15)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Sucesso")
                
                # Análise específica por endpoint
                if test['endpoint'] == '/':
                    if 'COSTAR' in response.text:
                        print("   ✅ Conteúdo COSTAR encontrado")
                    if 'javascript' in response.text.lower():
                        print("   ✅ JavaScript detectado")
                        
                elif response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if test['endpoint'] == '/api/generate-prompt':
                            if data.get('success'):
                                print("   ✅ Prompt gerado com sucesso")
                                prompt_preview = data.get('prompt', '')[:80] + '...'
                                print(f"   📝 Preview: {prompt_preview}")
                            else:
                                print(f"   ⚠️  Mensagem: {data.get('message', 'N/A')}")
                        else:
                            print(f"   📊 Dados: {list(data.keys())}")
                    except:
                        print("   📄 Resposta não-JSON")
                        
                results.append({"test": test['name'], "status": "✅ Passou"})
            else:
                print(f"   ❌ Falhou: {response.status_code}")
                results.append({"test": test['name'], "status": f"❌ Erro {response.status_code}"})
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Servidor não acessível") 
            results.append({"test": test['name'], "status": "❌ Conexão"})
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results.append({"test": test['name'], "status": f"❌ {str(e)[:30]}"})
    
    # Resumo final
    print("\n" + "="*50)
    print("📋 RESUMO DOS TESTES:")
    for result in results:
        print(f"   {result['test']}: {result['status']}")
    
    passed = len([r for r in results if "✅" in r['status']])
    total = len(results)
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 FRONTEND FUNCIONANDO PERFEITAMENTE!")
    elif passed > total/2:
        print("⚠️  FRONTEND FUNCIONANDO COM ALGUNS PROBLEMAS")
    else:
        print("❌ FRONTEND COM PROBLEMAS SÉRIOS")

if __name__ == "__main__":
    # Aguarda um pouco para o servidor inicializar
    time.sleep(3)
    test_frontend()