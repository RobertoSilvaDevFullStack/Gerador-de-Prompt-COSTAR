"""
🚀 Multi-AI Service OTIMIZADO para produção (Railway)
Versão simplificada e robusta com fallbacks
"""
import os
import json
import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionMultiAIService:
    """Serviço Multi-IA otimizado para produção"""
    
    def __init__(self):
        self.providers = self._load_providers()
        self.current_provider = "groq"  # Provider principal
        logger.info(f"🚀 ProductionMultiAIService inicializado com {len(self.providers)} provedores")
        
    def _load_providers(self) -> Dict[str, Dict[str, Any]]:
        """Carrega provedores disponíveis"""
        providers = {}
        
        # GROQ (Principal - Mais confiável)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            providers["groq"] = {
                "name": "Groq",
                "api_key": groq_key,
                "endpoint": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama3-8b-8192",
                "priority": 1
            }
            
        # GEMINI (Backup)
        if os.getenv("GEMINI_API_KEY"):
            providers["gemini"] = {
                "name": "Gemini",
                "api_key": os.getenv("GEMINI_API_KEY"),
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                "model": "gemini-pro",
                "priority": 2
            }
            
        # TOGETHER (Backup 2)
        if os.getenv("TOGETHER_API_KEY"):
            providers["together"] = {
                "name": "Together",
                "api_key": os.getenv("TOGETHER_API_KEY"),
                "endpoint": "https://api.together.xyz/v1/chat/completions",
                "model": "meta-llama/Llama-2-7b-chat-hf",
                "priority": 3
            }
            
        logger.info(f"🤖 Provedores carregados: {list(providers.keys())}")
        return providers
    
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Gera conteúdo usando o melhor provedor disponível"""
        
        logger.info(f"🎯 Iniciando geração de conteúdo. Provedores disponíveis: {len(self.providers)}")
        
        if not self.providers:
            logger.warning("⚠️ Nenhum provedor disponível, usando fallback")
            return self._fallback_response(prompt)
            
        # Tentar provedores em ordem de prioridade
        for provider_name in sorted(self.providers.keys(), 
                                   key=lambda x: self.providers[x]["priority"]):
            try:
                logger.info(f"🚀 Tentando provedor: {provider_name}")
                result = await self._try_provider(provider_name, prompt, **kwargs)
                if result:
                    logger.info(f"✅ Sucesso com {provider_name}")
                    return result
                else:
                    logger.warning(f"⚠️ {provider_name} retornou resultado vazio")
            except Exception as e:
                logger.error(f"❌ {provider_name} falhou: {str(e)}")
                continue
        
        # Se todos falharam, usar fallback
        logger.warning("⚠️ Todos os provedores falharam, usando fallback")
        return self._fallback_response(prompt)
        return self._fallback_response(prompt)
    
    async def _try_provider(self, provider_name: str, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Tenta usar um provedor específico"""
        provider = self.providers[provider_name]
        
        if provider_name == "groq":
            return await self._call_groq(provider, prompt, **kwargs)
        elif provider_name == "gemini":
            return await self._call_gemini(provider, prompt, **kwargs)
        elif provider_name == "together":
            return await self._call_together(provider, prompt, **kwargs)
            
        return None
    
    async def _call_groq(self, provider: Dict, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama API do Groq"""
        try:
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "model": provider["model"],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            logger.info(f"🌐 Chamando Groq API: {provider['endpoint']}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(provider["endpoint"], headers=headers, json=data)
                
                if response.status_code != 200:
                    logger.error(f"❌ Groq API erro {response.status_code}: {response.text}")
                    raise Exception(f"HTTP {response.status_code}")
                
                result = response.json()
                
                if "choices" not in result or not result["choices"]:
                    logger.error(f"❌ Groq resposta inválida: {result}")
                    raise Exception("Resposta inválida da API")
                
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"✅ Groq sucesso - {len(content)} caracteres")
                
                return {
                    "content": content,
                    "provider": "groq",
                    "model": provider["model"],
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na chamada Groq: {str(e)}")
            raise
    
    async def _call_gemini(self, provider: Dict, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama API do Gemini"""
        try:
            url = f"{provider['endpoint']}?key={provider['api_key']}"
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            logger.info(f"🌐 Chamando Gemini API: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=data)
                
                if response.status_code != 200:
                    logger.error(f"❌ Gemini API erro {response.status_code}: {response.text}")
                    raise Exception(f"HTTP {response.status_code}")
                
                result = response.json()
                
                if "candidates" not in result or not result["candidates"]:
                    logger.error(f"❌ Gemini resposta inválida: {result}")
                    raise Exception("Resposta inválida da API")
                
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                logger.info(f"✅ Gemini sucesso - {len(content)} caracteres")
                
                return {
                    "content": content,
                    "provider": "gemini",
                    "model": provider["model"],
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na chamada Gemini: {str(e)}")
            raise
    
    async def _call_together(self, provider: Dict, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama API do Together"""
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": provider["model"],
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(provider["endpoint"], headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return {
                "content": content,
                "provider": "together",
                "model": provider["model"],
                "success": True
            }
    
    def _fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Resposta de fallback quando todas as IAs falham"""
        logger.warning("🆘 Usando fallback - todas as IAs falharam")
        
        # Resposta básica estruturada
        fallback_content = f"""**PROMPT COSTAR GERADO** (Modo Básico)

{prompt}

---
*Nota: Este prompt foi gerado em modo básico. Para análises e melhorias com IA, verifique a configuração das APIs.*"""
        
        return {
            "content": fallback_content,
            "provider": "fallback",
            "model": "basic",
            "success": False,
            "message": "APIs de IA indisponíveis, usando modo básico"
        }

# Instância global para uso no projeto
multi_ai_service = ProductionMultiAIService()