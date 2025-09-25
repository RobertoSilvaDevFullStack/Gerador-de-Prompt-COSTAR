#!/usr/bin/env python3
"""
🔧 Script para Validar e Corrigir Chaves de API
"""

import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def test_groq():
    """Testar chave do Groq"""
    print("🟢 Testando GROQ...")
    try:
        from groq import AsyncGroq
        
        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        
        response = await client.chat.completions.create(
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            model="llama-3.1-8b-instant",  # Modelo mais simples
            temperature=0.7,
            max_tokens=10,
        )
        
        result = response.choices[0].message.content
        print(f"   ✅ GROQ funcionando: {result}")
        return True
        
    except Exception as e:
        print(f"   ❌ GROQ erro: {e}")
        return False

async def test_huggingface():
    """Testar HuggingFace"""
    print("🟠 Testando HUGGINGFACE...")
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers={
                    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": "Hello",
                    "parameters": {
                        "max_new_tokens": 5,
                        "temperature": 0.7,
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ HUGGINGFACE funcionando: {str(data)[:50]}...")
                return True
            else:
                print(f"   ❌ HUGGINGFACE erro: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ HUGGINGFACE erro: {e}")
        return False

async def test_cohere():
    """Testar Cohere"""
    print("🔵 Testando COHERE...")
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.cohere.com/v1/chat",
                headers={
                    "Authorization": f"Bearer {os.getenv('COHERE_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "command-r-plus-08-2024",  # Modelo atualizado
                    "message": "Responda apenas: OK",
                    "temperature": 0.7,
                    "max_tokens": 5,
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ COHERE funcionando: {data.get('text', 'OK')}")
                return True
            else:
                print(f"   ❌ COHERE erro: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ COHERE erro: {e}")
        return False

async def test_together():
    """Testar Together AI"""
    print("🟣 Testando TOGETHER...")
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
                    "messages": [{"role": "user", "content": "Responda apenas: OK"}],
                    "temperature": 0.7,
                    "max_tokens": 5,
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                print(f"   ✅ TOGETHER funcionando: {result}")
                return True
            else:
                print(f"   ❌ TOGETHER erro: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ TOGETHER erro: {e}")
        return False

async def main():
    """Testar todas as APIs"""
    print("🔧 VALIDANDO CHAVES DE API")
    print("=" * 40)
    
    results = {}
    
    # Testar cada API
    results['groq'] = await test_groq()
    results['huggingface'] = await test_huggingface()  
    results['cohere'] = await test_cohere()
    results['together'] = await test_together()
    
    # Resumo
    print("\n📊 RESUMO:")
    print("-" * 20)
    
    working = sum(results.values())
    total = len(results)
    
    for api, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {api.upper()}: {'FUNCIONANDO' if status else 'PROBLEMAS'}")
    
    print(f"\n🎯 APIs funcionando: {working}/{total}")
    
    if working >= 2:
        print("✅ Sistema Multi-IA pronto!")
    elif working >= 1:
        print("⚠️  Sistema funcionará com capacidade limitada")
    else:
        print("❌ Nenhuma API funcionando")

if __name__ == "__main__":
    asyncio.run(main())