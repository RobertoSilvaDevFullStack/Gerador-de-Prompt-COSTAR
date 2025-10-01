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
                "model": "llama-3.1-8b-instant",  # Modelo atual válido
                "priority": 1
            }
            
        # GEMINI (Backup)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            providers["gemini"] = {
                "name": "Gemini",
                "api_key": gemini_key,
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",  # Endpoint atualizado
                "model": "gemini-1.5-flash",  # Modelo atual válido
                "priority": 2
            }
            
        # TOGETHER (Backup 2)
        together_key = os.getenv("TOGETHER_API_KEY")
        if together_key:
            providers["together"] = {
                "name": "Together",
                "api_key": together_key,
                "endpoint": "https://api.together.xyz/v1/chat/completions",
                "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",  # Modelo atual válido
                "priority": 3
            }
            
        logger.info(f"🤖 Provedores carregados: {list(providers.keys())}")
        return providers
    
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Gera conteúdo usando o melhor provedor disponível"""
        
        logger.info(f"🎯 [PROD_AI] Iniciando geração de conteúdo")
        logger.info(f"📋 [PROD_AI] Provedores disponíveis: {len(self.providers)}")
        logger.info(f"🔑 [PROD_AI] Lista de provedores: {list(self.providers.keys())}")
        
        if not self.providers:
            logger.warning("⚠️ [PROD_AI] Nenhum provedor disponível, usando fallback")
            return self._fallback_response(prompt)
            
        # Tentar provedores em ordem de prioridade
        for provider_name in sorted(self.providers.keys(), 
                                   key=lambda x: self.providers[x]["priority"]):
            try:
                logger.info(f"🚀 [PROD_AI] Tentando provedor: {provider_name}")
                logger.info(f"🔑 [PROD_AI] API Key presente: {'✅' if self.providers[provider_name]['api_key'] else '❌'}")
                
                result = await self._try_provider(provider_name, prompt, **kwargs)
                if result:
                    logger.info(f"✅ [PROD_AI] SUCESSO com {provider_name}")
                    logger.info(f"📏 [PROD_AI] Tamanho da resposta: {len(result.get('content', ''))} chars")
                    return result
                else:
                    logger.warning(f"⚠️ [PROD_AI] {provider_name} retornou resultado vazio")
            except Exception as e:
                logger.error(f"❌ [PROD_AI] {provider_name} FALHOU: {str(e)}")
                logger.error(f"🔧 [PROD_AI] Tipo do erro: {type(e).__name__}")
                continue
        
        # Se todos falharam, usar fallback
        logger.warning("⚠️ [PROD_AI] TODOS os provedores falharam, usando fallback")
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
            logger.info(f"🌐 [GROQ] Iniciando chamada para Groq API")
            logger.info(f"🔗 [GROQ] Endpoint: {provider['endpoint']}")
            logger.info(f"🤖 [GROQ] Model: {provider['model']}")
            
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
            
            logger.info(f"📊 [GROQ] Payload: model={data['model']}, max_tokens={data['max_tokens']}, temp={data['temperature']}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info(f"📡 [GROQ] Enviando requisição...")
                response = await client.post(provider["endpoint"], headers=headers, json=data)
                
                logger.info(f"📨 [GROQ] Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ [GROQ] API erro {response.status_code}: {response.text}")
                    raise Exception(f"HTTP {response.status_code}")
                
                result = response.json()
                logger.info(f"📋 [GROQ] Estrutura da resposta: {list(result.keys()) if isinstance(result, dict) else 'não é dict'}")
                
                if "choices" not in result or not result["choices"]:
                    logger.error(f"❌ [GROQ] Resposta inválida: {result}")
                    raise Exception("Resposta inválida da API")
                
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"✅ [GROQ] Sucesso - {len(content)} caracteres gerados")
                logger.info(f"🎨 [GROQ] Preview: {content[:100]}...")
                
                return {
                    "content": content,
                    "provider": "groq",
                    "model": provider["model"],
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"❌ [GROQ] Erro na chamada: {str(e)}")
            logger.error(f"🔧 [GROQ] Tipo do erro: {type(e).__name__}")
            raise
    
    async def _call_gemini(self, provider: Dict, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama API do Gemini"""
        try:
            logger.info(f"💎 [GEMINI] Iniciando chamada para Gemini API")
            logger.info(f"🔗 [GEMINI] Endpoint: {provider['endpoint']}")
            logger.info(f"🤖 [GEMINI] Model: {provider['model']}")
            
            # Estrutura correta para Gemini v1beta
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            
            # URL com key como parâmetro
            url = f"{provider['endpoint']}?key={provider['api_key']}"
            
            logger.info(f"📊 [GEMINI] Config: maxTokens={data['generationConfig']['maxOutputTokens']}, temp={data['generationConfig']['temperature']}")
            logger.info(f"🔗 [GEMINI] URL: {url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info(f"📡 [GEMINI] Enviando requisição...")
                response = await client.post(url, json=data)
                
                logger.info(f"📨 [GEMINI] Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ [GEMINI] API erro {response.status_code}: {response.text}")
                    raise Exception(f"HTTP {response.status_code}")
                
                result = response.json()
                logger.info(f"📋 [GEMINI] Estrutura da resposta: {list(result.keys()) if isinstance(result, dict) else 'não é dict'}")
                
                if "candidates" not in result or not result["candidates"]:
                    logger.error(f"❌ [GEMINI] Resposta inválida: {result}")
                    raise Exception("Resposta inválida da API")
                
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                logger.info(f"✅ [GEMINI] Sucesso - {len(content)} caracteres gerados")
                logger.info(f"🎨 [GEMINI] Preview: {content[:100]}...")
                
                return {
                    "content": content,
                    "provider": "gemini",
                    "model": provider["model"],
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"❌ [GEMINI] Erro na chamada: {str(e)}")
            logger.error(f"🔧 [GEMINI] Tipo do erro: {type(e).__name__}")
            raise
    
    async def _call_together(self, provider: Dict, prompt: str, **kwargs) -> Dict[str, Any]:
        """Chama API do Together"""
        try:
            logger.info(f"🌐 [TOGETHER] Iniciando chamada para Together API")
            logger.info(f"🔗 [TOGETHER] Endpoint: {provider['endpoint']}")
            logger.info(f"🤖 [TOGETHER] Model: {provider['model']}")
            
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
            
            logger.info(f"📊 [TOGETHER] Payload: model={data['model']}, max_tokens={data['max_tokens']}, temp={data['temperature']}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info(f"📡 [TOGETHER] Enviando requisição...")
                response = await client.post(provider["endpoint"], headers=headers, json=data)
                
                logger.info(f"📨 [TOGETHER] Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ [TOGETHER] API erro {response.status_code}: {response.text}")
                    raise Exception(f"HTTP {response.status_code}")
                
                result = response.json()
                logger.info(f"📋 [TOGETHER] Estrutura da resposta: {list(result.keys()) if isinstance(result, dict) else 'não é dict'}")
                
                if "choices" not in result or not result["choices"]:
                    logger.error(f"❌ [TOGETHER] Resposta inválida: {result}")
                    raise Exception("Resposta inválida da API")
                
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"✅ [TOGETHER] Sucesso - {len(content)} caracteres gerados")
                logger.info(f"🎨 [TOGETHER] Preview: {content[:100]}...")
                
                return {
                    "content": content,
                    "provider": "together",
                    "model": provider["model"],
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"❌ [TOGETHER] Erro na chamada: {str(e)}")
            logger.error(f"🔧 [TOGETHER] Tipo do erro: {type(e).__name__}")
            raise
        
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

# Instância global para uso no projeto (lazy loading)
_multi_ai_service = None

def get_multi_ai_service():
    """Obter instância do multi_ai_service com lazy loading"""
    global _multi_ai_service
    if _multi_ai_service is None:
        _multi_ai_service = ProductionMultiAIService()
        logger.info("🚀 ProductionMultiAIService inicializado (lazy loading)")
    return _multi_ai_service

# Compatibilidade com código existente - inicialização no import
try:
    multi_ai_service = get_multi_ai_service()
except Exception as e:
    logger.error(f"❌ Erro na inicialização do multi_ai_service: {e}")
    multi_ai_service = None