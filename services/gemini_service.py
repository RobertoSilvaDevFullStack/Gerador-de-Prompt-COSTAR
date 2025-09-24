import os
import httpx
from typing import Dict, Any, Optional
import asyncio
import json

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY não configurada")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"
    
    async def generate_content(
        self,
        prompt: str,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Gerar conteúdo usando Gemini via API REST"""
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperatura,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": max_tokens,
                }
            }
            
            params = {"key": self.api_key}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers, params=params)
                
                if response.status_code != 200:
                    error_text = response.text
                    raise Exception(f"Erro na API do Gemini: {response.status_code} - {error_text}")
                
                result = response.json()
                
                # Extrair texto da resposta
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return parts[0]["text"]
                
                raise Exception("Resposta inválida da API do Gemini")
                
        except httpx.TimeoutException:
            raise Exception("Timeout na requisição para o Gemini")
        except Exception as e:
            raise Exception(f"Erro ao gerar conteúdo: {str(e)}")
    
    async def analyze_prompt_quality(self, prompt: str) -> Dict[str, Any]:
        """Analisar qualidade do prompt usando Gemini"""
        try:
            analysis_prompt = f"""
Você é um especialista em prompt engineering. Analise a qualidade do seguinte prompt COSTAR:

PROMPT A ANALISAR:
{prompt}

Forneça uma análise detalhada no formato JSON exato abaixo (sem texto adicional):

{{
    "pontuacao": [número de 1-100],
    "qualidade": "[Excelente|Boa|Regular|Precisa melhorar]",
    "pontos_fortes": [
        "lista de pontos fortes específicos"
    ],
    "areas_melhoria": [
        "lista de áreas que precisam melhorar"
    ],
    "sugestoes": [
        "sugestões específicas e acionáveis"
    ],
    "resumo": "resumo em uma frase da qualidade geral",
    "detalhes_tecnicos": {{
        "clareza": [1-10],
        "especificidade": [1-10], 
        "completude": [1-10],
        "coerencia": [1-10]
    }}
}}

IMPORTANTE: Retorne APENAS o JSON, sem explicações adicionais.
"""
            
            result = await self.generate_content(analysis_prompt, temperatura=0.3)
            
            # Tentar parsear JSON do resultado
            try:
                # Limpar o resultado e extrair apenas o JSON
                clean_result = result.strip()
                
                # Procurar pelo JSON
                start = clean_result.find('{')
                end = clean_result.rfind('}') + 1
                
                if start != -1 and end > start:
                    json_str = clean_result[start:end]
                    parsed = json.loads(json_str)
                    return parsed
                else:
                    # Fallback se não conseguir parsear
                    return {
                        "pontuacao": 75,
                        "qualidade": "Boa",
                        "pontos_fortes": ["Prompt estruturado"],
                        "areas_melhoria": ["Parsing automático falhou"],
                        "sugestoes": ["Análise manual recomendada"],
                        "resumo": "Análise automática com limitações",
                        "feedback_raw": result[:500],
                        "modo": "fallback"
                    }
            except json.JSONDecodeError as e:
                return {
                    "pontuacao": 70,
                    "qualidade": "Regular", 
                    "pontos_fortes": ["Resposta gerada com sucesso"],
                    "areas_melhoria": ["Formato JSON inválido"],
                    "sugestoes": ["Revisar prompt de análise"],
                    "resumo": "Erro no parsing da análise",
                    "feedback_raw": result[:500],
                    "erro_parsing": str(e)
                }
                
        except Exception as e:
            return {
                "pontuacao": 50,
                "qualidade": "Erro",
                "erro": f"Erro ao analisar prompt: {str(e)}",
                "resumo": "Falha na análise via IA"
            }

    async def test_connection(self) -> Dict[str, Any]:
        """Testar conexão com a API do Gemini"""
        try:
            test_prompt = "Responda apenas 'OK' se você está funcionando."
            result = await self.generate_content(test_prompt, max_tokens=10)
            return {
                "status": "success",
                "response": result.strip(),
                "working": "OK" in result.upper()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }