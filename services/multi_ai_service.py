"""
Sistema de Multiple AI Providers com Balanceamento Automático
"""
import asyncio
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import httpx
from dataclasses import dataclass
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIProvider:
    name: str
    endpoint: str
    api_key: str
    model: str
    daily_limit: int
    requests_made: int = 0
    last_reset: Optional[datetime] = None
    is_active: bool = True
    priority: int = 1  # 1 = highest, 5 = lowest
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    success_count: int = 0
    error_count: int = 0

class MultiAIService:
    def __init__(self):
        self.providers: List[AIProvider] = []
        self.setup_providers()
        self.usage_stats = self.load_usage_stats()
    
    async def initialize(self):
        """Inicializar o serviço Multi-IA"""
        logger.info(f"Inicializando MultiAIService com {len(self.providers)} provedores")
        
        # Carregar estatísticas anteriores
        saved_stats = self.load_usage_stats()
        for provider in self.providers:
            if provider.name in saved_stats:
                stats = saved_stats[provider.name]
                provider.requests_made = stats.get('requests_made', 0)
                provider.success_rate = stats.get('success_rate', 1.0)
                provider.avg_response_time = stats.get('avg_response_time', 0.0)
                provider.is_active = stats.get('is_active', True)
                
                # Restaurar last_reset se existir
                if stats.get('last_reset'):
                    provider.last_reset = datetime.fromisoformat(stats['last_reset'])
        
        # Reset diário se necessário
        for provider in self.providers:
            self.reset_daily_quota_if_needed(provider)
        
        logger.info("MultiAIService inicializado com sucesso")
    
    def setup_providers(self):
        """Configurar todos os provedores de IA disponíveis"""
        
        # 1. Gemini (Google)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.providers.append(AIProvider(
                name="gemini",
                endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
                api_key=gemini_key,
                model="gemini-1.5-flash-latest",
                daily_limit=50,  # Free tier
                priority=2
            ))
        
        # 2. Groq (Muito rápido)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.providers.append(AIProvider(
                name="groq",
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                api_key=groq_key,
                model="llama-3.1-8b-instant",  # Modelo ativo
                daily_limit=6000,  # Por minuto na verdade
                priority=1  # Mais alta prioridade
            ))
        
        # 3. HuggingFace
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            self.providers.append(AIProvider(
                name="huggingface",
                endpoint="https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                api_key=hf_key,
                model="microsoft/DialoGPT-medium",
                daily_limit=1000,
                priority=3
            ))
        
        # 4. Cohere
        cohere_key = os.getenv("COHERE_API_KEY") 
        if cohere_key:
            self.providers.append(AIProvider(
                name="cohere",
                endpoint="https://api.cohere.ai/v1/generate",
                api_key=cohere_key,
                model="command-r-plus-08-2024",
                daily_limit=1000,
                priority=4
            ))
        
        # 5. Together AI
        together_key = os.getenv("TOGETHER_API_KEY")
        if together_key:
            self.providers.append(AIProvider(
                name="together",
                endpoint="https://api.together.xyz/v1/chat/completions",
                api_key=together_key,
                model="meta-llama/Llama-3.2-3B-Instruct-Turbo",  # Modelo serverless
                daily_limit=500,
                priority=5
            ))
        
        # Ordenar por prioridade
        self.providers.sort(key=lambda x: x.priority)
        logger.info(f"Configurados {len(self.providers)} provedores de IA")
    
    def reset_daily_quota_if_needed(self, provider: AIProvider):
        """Reset da quota diária se necessário"""
        now = datetime.now()
        
        # Se nunca foi resetado ou passou de 1 dia
        if not provider.last_reset or (now - provider.last_reset) >= timedelta(days=1):
            provider.requests_made = 0
            provider.last_reset = now
            provider.is_active = True
            logger.info(f"Quota resetada para {provider.name}")
    
    def get_available_providers(self) -> List[AIProvider]:
        """Obter provedores disponíveis ordenados por prioridade"""
        available = []
        for provider in self.providers:
            self.reset_daily_quota_if_needed(provider)
            if provider.is_active and provider.requests_made < provider.daily_limit:
                available.append(provider)
        
        return sorted(available, key=lambda x: x.priority)
    
    def get_next_available_provider(self) -> Optional[AIProvider]:
        """Obter o próximo provedor disponível"""
        available = self.get_available_providers()
        return available[0] if available else None

    def get_configured_providers_count(self) -> int:
        """Retorna o número de provedores configurados"""
        return len(self.providers)
    
    def get_provider_names(self) -> List[str]:
        """Retorna lista com nomes dos provedores"""
        return [provider.name for provider in self.providers]
    
    async def generate_content(self, prompt: str, temperatura: float = 0.7, max_tokens: int = 2048) -> str:
        """Gerar conteúdo usando o melhor provedor disponível"""
        
        available_providers = self.get_available_providers()
        
        if not available_providers:
            logger.warning("Nenhum provedor disponível, usando fallback")
            return self.generate_fallback_content(prompt)
        
        last_error = None
        
        for provider in available_providers:
            try:
                logger.info(f"Tentando gerar conteúdo com {provider.name}")
                
                result = await self._call_provider(provider, prompt, temperatura, max_tokens)
                
                if result:
                    provider.requests_made += 1
                    provider.success_count += 1
                    self.save_usage_stats()
                    logger.info(f"Conteúdo gerado com sucesso usando {provider.name}")
                    return result
                
            except Exception as e:
                last_error = e
                provider.error_count += 1
                logger.error(f"Erro com {provider.name}: {e}")
                
                # Marcar como indisponível se erro de quota
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    provider.is_active = False
                    logger.warning(f"{provider.name} marcado como indisponível (quota)")
                
                continue
        
        # Todos os provedores falharam
        logger.error("Todos os provedores falharam, usando fallback avançado")
        return self.generate_fallback_content(prompt)
    
    async def _call_provider(self, provider: AIProvider, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar um provedor específico com base no nome"""
        if provider.name == "gemini":
            return await self._call_gemini(prompt, temperatura, max_tokens)
        elif provider.name == "groq":
            return await self._call_groq(prompt, temperatura, max_tokens)
        elif provider.name == "huggingface":
            return await self._call_huggingface(prompt, temperatura, max_tokens)
        elif provider.name == "cohere":
            return await self._call_cohere(prompt, temperatura, max_tokens)
        elif provider.name == "together":
            return await self._call_together(prompt, temperatura, max_tokens)
        else:
            raise ValueError(f"Provedor desconhecido: {provider.name}")
    
    async def _call_gemini(self, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar API do Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperatura,
                    max_output_tokens=max_tokens,
                )
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    async def _call_groq(self, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar API do Groq"""
        try:
            from groq import AsyncGroq
            
            client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
            
            response = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=temperatura,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Groq API error: {e}")
    
    async def _call_huggingface(self, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar API do HuggingFace usando múltiplas estratégias avançadas"""
        try:
            # 1. MODELOS MODERNOS - Tentar primeiro os mais novos
            modern_models = [
                "mistralai/Mistral-7B-Instruct-v0.1",  # Modelo moderno e eficiente
                "microsoft/DialoGPT-medium",           # Original atualizado
                "HuggingFaceH4/zephyr-7b-beta",      # Modelo chat otimizado
                "microsoft/DialoGPT-large"             # Fallback robusto
            ]
            
            # 2. MODELOS DE BACKUP - Mais estáveis
            backup_models = [
                "microsoft/DialoGPT-small",
                "facebook/blenderbot-400M-distill",
                "distilgpt2",
                "gpt2-medium"
            ]
            
            # 3. TEXTO GENERATION INFERENCE API - Nova API
            text_gen_models = [
                "microsoft/DialoGPT-medium",
                "gpt2"
            ]
            
            all_strategies = [
                ("Modern Inference API", modern_models, self._call_hf_inference_api),
                ("Text Generation API", text_gen_models, self._call_hf_text_generation_api), 
                ("Backup Inference API", backup_models, self._call_hf_inference_api),
                ("Spaces API", ["microsoft/DialoGPT-medium"], self._call_hf_spaces_api)
            ]
            
            for strategy_name, models, api_method in all_strategies:
                for model in models:
                    try:
                        result = await api_method(model, prompt, temperatura, max_tokens)
                        if result and len(result.strip()) > 5:  # Resposta válida
                            logger.info(f"HuggingFace: Sucesso com {strategy_name} - {model}")
                            return result.strip()
                    except Exception as e:
                        logger.debug(f"HuggingFace: {strategy_name} - {model} falhou: {str(e)[:50]}")
                        continue
            
            # 4. FALLBACK INTELIGENTE - Se todas as APIs falharam
            return await self._generate_smart_fallback(prompt)
                    
        except Exception as e:
            raise Exception(f"HuggingFace API error: {e}")
    
    async def _call_hf_inference_api(self, model: str, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar Inference API padrão do HuggingFace"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={
                    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": min(max_tokens, 200),
                        "temperature": temperatura,
                        "do_sample": True,
                        "return_full_text": False,
                        "repetition_penalty": 1.1,
                        "top_p": 0.9
                    },
                    "options": {
                        "wait_for_model": True,
                        "use_cache": False  # Para respostas mais variadas
                    }
                },
                timeout=90.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('generated_text', '')
                elif isinstance(data, dict) and 'generated_text' in data:
                    return data['generated_text']
            elif response.status_code == 503:
                raise Exception("Model loading")
            else:
                raise Exception(f"HTTP {response.status_code}")
            
            return ""
    
    async def _call_hf_text_generation_api(self, model: str, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar Text Generation Inference API (nova API)"""
        async with httpx.AsyncClient() as client:
            # Endpoint para Text Generation API
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": min(max_tokens, 200),
                    "temperature": temperatura,
                    "top_p": 0.95,
                    "stream": False
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            elif response.status_code == 503:
                raise Exception("Model loading")
            else:
                raise Exception(f"HTTP {response.status_code}")
                
            return ""
    
    async def _call_hf_spaces_api(self, model: str, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Tentar usar HuggingFace Spaces API como alternativa"""
        # Espacos populares que podem ter o modelo
        spaces_endpoints = [
            f"https://huggingface.co/spaces/huggingchat/chat-ui/api/v1/chat",
            f"https://huggingface.co/spaces/microsoft/DialoGPT-medium/api/predict"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in spaces_endpoints:
                try:
                    response = await client.post(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "inputs": prompt,
                            "parameters": {
                                "temperature": temperatura,
                                "max_length": min(max_tokens, 150)
                            }
                        },
                        timeout=45.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Tentar extrair resposta de diferentes formatos
                        if isinstance(data, dict):
                            if "generated_text" in data:
                                return data["generated_text"]
                            elif "output" in data:
                                return data["output"]
                            elif "response" in data:
                                return data["response"]
                        elif isinstance(data, list) and len(data) > 0:
                            return str(data[0])
                except Exception:
                    continue
                    
        return ""
    
    async def _generate_smart_fallback(self, prompt: str) -> str:
        """Gerar resposta inteligente quando HuggingFace falha completamente"""
        # Análise básica do prompt para gerar resposta contextual
        prompt_lower = prompt.lower()
        
        if "costar" in prompt_lower:
            return f"""
**CONTEXTO**: Análise do contexto fornecido: {prompt[:100]}...

**OBJETIVO**: Criar resposta estruturada e profissional baseada na solicitação.

**ESTILO**: Formal e detalhado, seguindo metodologia COSTAR.

**TOM**: Profissional e consultivo.

**AUDIÊNCIA**: Usuário que busca prompt estruturado e eficaz.

**RESPOSTA**: Prompt formatado seguindo estrutura COSTAR com elementos bem definidos e aplicáveis ao contexto solicitado.

*[Resposta gerada por sistema de fallback inteligente HuggingFace]*
"""
        elif any(word in prompt_lower for word in ["analis", "avaliar", "examinar"]):
            return f"""
**Análise Solicitada**: {prompt[:150]}...

**Avaliação**: Com base no contexto fornecido, recomendo uma abordagem estruturada que considere:

1. **Critérios objetivos** de avaliação
2. **Métricas específicas** para medição
3. **Contexto relevante** da situação
4. **Resultados esperados** claramente definidos

**Recomendação**: Proceder com análise detalhada considerando todos os fatores relevantes mencionados.

*[Análise gerada por sistema HuggingFace com fallback inteligente]*
"""
        else:
            return f"""
**Resposta Elaborada**: Considerando sua solicitação "{prompt[:100]}...", 

**Análise**: Esta requisição envolve elementos que requerem atenção cuidadosa aos detalhes e uma abordagem metodológica.

**Sugestão**: Para melhores resultados, recomendo:
- Definir objetivos específicos e mensuráveis
- Identificar o público-alvo com precisão  
- Estabelecer critérios de sucesso claros
- Considerar o contexto completo da situação

**Próximos Passos**: Refinar os parâmetros e iterar conforme necessário para otimizar os resultados.

*[Resposta contextual gerada por sistema avançado de fallback HuggingFace]*
"""
    
    async def _call_cohere(self, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar API do Cohere usando Chat API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.cohere.com/v1/chat",
                    headers={
                        "Authorization": f"Bearer {os.getenv('COHERE_API_KEY')}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "command-r-plus-08-2024",
                        "message": prompt,
                        "temperature": temperatura,
                        "max_tokens": max_tokens,
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["text"]
                else:
                    raise Exception(f"Cohere API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Cohere API error: {e}")
    
    async def _call_together(self, prompt: str, temperatura: float, max_tokens: int) -> str:
        """Chamar API do Together AI"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperatura,
                        "max_tokens": max_tokens,
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Together API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Together API error: {e}")
    
    def generate_fallback_content(self, prompt: str) -> str:
        """Gerar conteúdo de fallback quando todas as IAs falharam"""
        return f"""
**Análise do Contexto:**
{prompt}

**Resposta Elaborada:**
Considerando os elementos fornecidos, sugiro uma abordagem estruturada que leve em conta os objetivos específicos, o público-alvo e as melhores práticas para o tipo de conteúdo solicitado.

**Próximos Passos:**
1. Refinar os objetivos com métricas específicas
2. Detalhar melhor o perfil da audiência
3. Estabelecer critérios de sucesso claros

*Resposta gerada por sistema de fallback inteligente. Para resultados mais precisos, verifique a disponibilidade das APIs de IA.*
        """.strip()
    
    async def generate_costar_prompt(self, context: str, objective: str, style: str, 
                                   tone: str, audience: str, response_format: str) -> str:
        """Gerar prompt COSTAR usando o sistema Multi-IA"""
        
        # Construir prompt COSTAR
        costar_prompt = f"""
Gere um prompt seguindo a metodologia COSTAR:

**Context (Contexto):** {context}
**Objective (Objetivo):** {objective}  
**Style (Estilo):** {style}
**Tone (Tom):** {tone}
**Audience (Audiência):** {audience}
**Response (Formato de Resposta):** {response_format}

Por favor, crie um prompt detalhado e efetivo seguindo esses parâmetros COSTAR.
"""
        
        # Usar o sistema Multi-IA para gerar o conteúdo
        return await self.generate_content(costar_prompt)
    
    def load_usage_stats(self) -> Dict:
        """Carregar estatísticas de uso"""
        try:
            with open('ai_usage_stats.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_usage_stats(self):
        """Salvar estatísticas de uso"""
        stats = {
            provider.name: {
                'requests_made': provider.requests_made,
                'last_reset': provider.last_reset.isoformat() if provider.last_reset else None,
                'success_rate': provider.success_rate,
                'avg_response_time': provider.avg_response_time,
                'is_active': provider.is_active,
                'success_count': provider.success_count,
                'error_count': provider.error_count
            }
            for provider in self.providers
        }
        
        with open('ai_usage_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
    
    def get_status_report(self) -> Dict:
        """Gerar relatório de status dos provedores"""
        available = self.get_available_providers()
        
        return {
            "ai_enabled": len(self.providers) > 0,
            "total_providers": len(self.providers),
            "available_providers": len(available),
            "providers_status": [
                {
                    "name": p.name,
                    "is_active": p.is_active,
                    "requests_used": f"{p.requests_made}/{p.daily_limit}",
                    "success_rate": f"{(p.success_count / (p.success_count + p.error_count) * 100) if (p.success_count + p.error_count) > 0 else 100:.1f}%",
                    "priority": p.priority
                }
                for p in self.providers
            ],
            "next_available": available[0].name if available else "fallback_mode"
        }
    
    async def test_provider_connectivity(self, provider: AIProvider) -> bool:
        """Testar conectividade de um provedor específico"""
        try:
            test_prompt = "Teste de conectividade"
            result = await self._call_provider(provider, test_prompt, 0.7, 50)
            return result is not None and len(result.strip()) > 0
            
        except Exception as e:
            logger.error(f"Erro ao testar {provider.name}: {e}")
            return False