"""
Serviço integrado para gerenciamento de dados - Supabase + Demo Mode
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel

# Importações condicionais do Supabase
try:
    from services.supabase_base_service import SupabaseService
    from config.supabase_config import get_config, check_configuration
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

class DataService:
    """Serviço integrado de dados - Supabase ou Demo"""
    
    def __init__(self):
        """Inicializa o serviço de dados"""
        self.mode = "demo"  # Padrão demo
        self.supabase_service = None
        self.demo_data = {
            'prompts': [],
            'templates': [],
            'users': {},
            'ratings': [],
            'ai_logs': [],
            'settings': {}
        }
        
        # Tenta inicializar Supabase
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Inicializa conexão Supabase se disponível"""
        
        if not SUPABASE_AVAILABLE:
            print("ℹ️  Supabase não disponível - usando modo demo")
            return
        
        try:
            config_check = check_configuration()
            if config_check['ready_for_public']:
                self.supabase_service = SupabaseService()
                # Testa se consegue conectar de verdade
                test_result = self.supabase_service.test_connection()
                if test_result.get('status') == 'connected':
                    self.mode = "supabase"
                    print("✅ Supabase inicializado e conectado com sucesso")
                else:
                    print(f"⚠️  Supabase configurado mas sem conexão: {test_result.get('message', 'erro desconhecido')} - usando modo demo")
            else:
                print("ℹ️  Supabase não configurado - usando modo demo")
        except Exception as e:
            print(f"⚠️  Erro ao inicializar Supabase: {e} - usando modo demo")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Testa conexão com o backend"""
        if self.mode == "supabase" and self.supabase_service:
            try:
                connection_result = self.supabase_service.test_connection()
                return {
                    'mode': 'supabase',
                    'connected': connection_result.get('status') == 'connected',
                    'status': connection_result.get('status', 'unknown'),
                    'message': connection_result.get('message', '')
                }
            except Exception as e:
                return {
                    'mode': 'supabase',
                    'connected': False,
                    'status': f'error: {e}'
                }
        else:
            return {
                'mode': 'demo',
                'connected': True,
                'status': 'demo_mode_active'
            }
    
    # ==================== PROMPTS ====================
    
    def save_prompt(self, user_id: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva um prompt"""
        if self.mode == "supabase":
            return self._save_prompt_supabase(user_id, prompt_data)
        else:
            return self._save_prompt_demo(user_id, prompt_data)
    
    def get_user_prompts(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Busca prompts do usuário"""
        if self.mode == "supabase":
            return self._get_user_prompts_supabase(user_id, limit, offset)
        else:
            return self._get_user_prompts_demo(user_id, limit, offset)
    
    def delete_prompt(self, user_id: str, prompt_id: str) -> bool:
        """Deleta um prompt"""
        if self.mode == "supabase":
            return self._delete_prompt_supabase(user_id, prompt_id)
        else:
            return self._delete_prompt_demo(user_id, prompt_id)
    
    # ==================== TEMPLATES ====================
    
    async def get_public_templates(self, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca templates públicos"""
        if self.mode == "supabase":
            return await self._get_public_templates_supabase(category, limit)
        else:
            return self._get_public_templates_demo(category, limit)
    
    async def save_template(self, user_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva um template"""
        if self.mode == "supabase":
            return await self._save_template_supabase(user_id, template_data)
        else:
            return self._save_template_demo(user_id, template_data)
    
    # ==================== ANÁLISES/LOGS ====================
    
    async def log_ai_usage(self, user_id: str, provider: str, tokens_used: int, cost: float = 0.0) -> bool:
        """Registra uso de IA"""
        if self.mode == "supabase":
            return await self._log_ai_usage_supabase(user_id, provider, tokens_used, cost)
        else:
            return self._log_ai_usage_demo(user_id, provider, tokens_used, cost)
    
    async def get_ai_usage_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Busca estatísticas de uso de IA"""
        if self.mode == "supabase":
            return await self._get_ai_usage_stats_supabase(user_id, days)
        else:
            return self._get_ai_usage_stats_demo(user_id, days)
    
    # ==================== IMPLEMENTAÇÕES SUPABASE ====================
    
    def _save_prompt_supabase(self, user_id: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva prompt no Supabase"""
        try:
            data = {
                'user_id': user_id,
                'title': prompt_data.get('titulo', 'Prompt sem título'),
                'context': prompt_data.get('contexto', ''),
                'objective': prompt_data.get('objetivo', ''),
                'style': prompt_data.get('estilo', ''),
                'tone': prompt_data.get('tom', ''),
                'audience': prompt_data.get('audiencia', ''),
                'response': prompt_data.get('resposta', ''),
                'category': prompt_data.get('categoria', 'geral'),
                'tags': prompt_data.get('tags', []),
                'is_favorite': prompt_data.get('favorito', False),
                'is_shared': prompt_data.get('compartilhado', False)
            }
            
            result = self.supabase_service.table_operation('prompts', 'insert', data=data)
            
            if result['success'] and result['data']:
                saved_prompt = result['data'][0]
                return {
                    'success': True,
                    'id': saved_prompt['id'],
                    'created_at': saved_prompt['created_at']
                }
            else:
                return {'success': False, 'error': result.get('error', 'Erro desconhecido')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_user_prompts_supabase(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Busca prompts do usuário no Supabase"""
        try:
            # Como o Supabase Python não suporta LIMIT/OFFSET direto na table operation,
            # vamos buscar todos e fazer slice em Python por enquanto
            result = self.supabase_service.table_operation(
                'prompts', 
                'select', 
                filters={'user_id': user_id}
            )
            
            if result['success']:
                # Ordena por created_at (assumindo que existe) e aplica paginação
                prompts = result['data']
                prompts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                return prompts[offset:offset + limit]
            else:
                print(f"Erro ao buscar prompts: {result.get('error')}")
                return []
                
        except Exception as e:
            print(f"Exceção ao buscar prompts: {e}")
            return []
    
    def _delete_prompt_supabase(self, user_id: str, prompt_id: str) -> bool:
        """Deleta prompt no Supabase"""
        try:
            result = self.supabase_service.table_operation(
                'prompts', 
                'delete', 
                filters={'id': prompt_id, 'user_id': user_id}
            )
            return result['success']
        except Exception as e:
            print(f"Erro ao deletar prompt: {e}")
            return False
    
    async def _get_public_templates_supabase(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Busca templates públicos no Supabase"""
        try:
            if category:
                query = """
                SELECT id, title, description, context_template, objective_template, 
                       style_template, tone_template, audience_template, category, 
                       tags, created_at, avg_rating, usage_count
                FROM prompt_templates 
                WHERE category = $1 AND is_active = true
                ORDER BY avg_rating DESC, usage_count DESC
                LIMIT $2;
                """
                params = [category, limit]
            else:
                query = """
                SELECT id, title, description, context_template, objective_template, 
                       style_template, tone_template, audience_template, category, 
                       tags, created_at, avg_rating, usage_count
                FROM prompt_templates 
                WHERE is_active = true
                ORDER BY avg_rating DESC, usage_count DESC
                LIMIT $1;
                """
                params = [limit]
            
            result = await self.supabase_service.execute_query(query, params=params)
            return result['data'] if result['success'] else []
            
        except Exception as e:
            print(f"Erro ao buscar templates: {e}")
            return []
    
    async def _save_template_supabase(self, user_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva template no Supabase"""
        try:
            query = """
            INSERT INTO prompt_templates (created_by, title, description, context_template, 
                                        objective_template, style_template, tone_template, 
                                        audience_template, category, tags)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id, created_at;
            """
            
            params = [
                user_id,
                template_data.get('titulo', 'Template sem título'),
                template_data.get('descricao', ''),
                template_data.get('contexto_template', ''),
                template_data.get('objetivo_template', ''),
                template_data.get('estilo_template', ''),
                template_data.get('tom_template', ''),
                template_data.get('audiencia_template', ''),
                template_data.get('categoria', 'geral'),
                template_data.get('tags', [])
            ]
            
            result = await self.supabase_service.execute_query(query, params=params)
            
            if result['success'] and result['data']:
                saved_template = result['data'][0]
                return {
                    'success': True,
                    'id': saved_template['id'],
                    'created_at': saved_template['created_at']
                }
            else:
                return {'success': False, 'error': result.get('error', 'Erro desconhecido')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _log_ai_usage_supabase(self, user_id: str, provider: str, tokens_used: int, cost: float) -> bool:
        """Registra uso de IA no Supabase"""
        try:
            query = """
            INSERT INTO ai_usage_logs (user_id, provider, tokens_used, estimated_cost, endpoint_used)
            VALUES ($1, $2, $3, $4, 'costar_generation');
            """
            
            params = [user_id, provider, tokens_used, cost]
            result = await self.supabase_service.execute_query(query, params=params)
            return result['success']
            
        except Exception as e:
            print(f"Erro ao registrar uso de IA: {e}")
            return False
    
    async def _get_ai_usage_stats_supabase(self, user_id: str, days: int) -> Dict[str, Any]:
        """Busca estatísticas de uso de IA no Supabase"""
        try:
            query = """
            SELECT provider, 
                   COUNT(*) as request_count,
                   SUM(tokens_used) as total_tokens,
                   SUM(estimated_cost) as total_cost
            FROM ai_usage_logs 
            WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
            GROUP BY provider
            ORDER BY total_tokens DESC;
            """ % days
            
            result = await self.supabase_service.execute_query(query, params=[user_id])
            
            if result['success']:
                return {
                    'period_days': days,
                    'providers': result['data'],
                    'total_requests': sum(p['request_count'] for p in result['data']),
                    'total_tokens': sum(p['total_tokens'] for p in result['data']),
                    'total_cost': sum(p['total_cost'] for p in result['data'])
                }
            else:
                return {'period_days': days, 'providers': [], 'total_requests': 0, 'total_tokens': 0, 'total_cost': 0}
                
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return {'period_days': days, 'providers': [], 'total_requests': 0, 'total_tokens': 0, 'total_cost': 0}
    
    # ==================== IMPLEMENTAÇÕES DEMO ====================
    
    def _save_prompt_demo(self, user_id: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva prompt no modo demo"""
        prompt_id = f"demo_prompt_{len(self.demo_data['prompts']) + 1}"
        timestamp = datetime.now().isoformat()
        
        demo_prompt = {
            'id': prompt_id,
            'user_id': user_id,
            'title': prompt_data.get('titulo', 'Prompt sem título'),
            'contexto': prompt_data.get('contexto', ''),
            'objetivo': prompt_data.get('objetivo', ''),
            'estilo': prompt_data.get('estilo', ''),
            'tom': prompt_data.get('tom', ''),
            'audiencia': prompt_data.get('audiencia', ''),
            'resposta': prompt_data.get('resposta', ''),
            'categoria': prompt_data.get('categoria', 'geral'),
            'tags': prompt_data.get('tags', []),
            'favorito': prompt_data.get('favorito', False),
            'compartilhado': prompt_data.get('compartilhado', False),
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        self.demo_data['prompts'].append(demo_prompt)
        
        return {
            'success': True,
            'id': prompt_id,
            'created_at': timestamp
        }
    
    def _get_user_prompts_demo(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Busca prompts do usuário no modo demo"""
        user_prompts = [p for p in self.demo_data['prompts'] if p['user_id'] == user_id]
        user_prompts.sort(key=lambda x: x['created_at'], reverse=True)
        return user_prompts[offset:offset + limit]
    
    def _delete_prompt_demo(self, user_id: str, prompt_id: str) -> bool:
        """Deleta prompt no modo demo"""
        for i, prompt in enumerate(self.demo_data['prompts']):
            if prompt['id'] == prompt_id and prompt['user_id'] == user_id:
                self.demo_data['prompts'].pop(i)
                return True
        return False
    
    def _get_public_templates_demo(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Busca templates públicos no modo demo"""
        # Templates de exemplo para demo
        demo_templates = [
            {
                'id': 'template_1',
                'title': 'Email Profissional',
                'description': 'Template para emails corporativos',
                'category': 'comunicacao',
                'context_template': 'Comunicação empresarial formal',
                'objective_template': 'Transmitir informações importantes de forma clara',
                'style_template': 'Formal e respeitoso',
                'tone_template': 'Profissional',
                'audience_template': 'Colegas de trabalho e clientes',
                'tags': ['email', 'formal', 'trabalho'],
                'avg_rating': 4.5,
                'usage_count': 150
            },
            {
                'id': 'template_2',
                'title': 'Post para Redes Sociais',
                'description': 'Template para posts engajadores',
                'category': 'marketing',
                'context_template': 'Promoção de conteúdo nas redes sociais',
                'objective_template': 'Aumentar engajamento e alcance',
                'style_template': 'Casual e criativo',
                'tone_template': 'Amigável e entusiástico',
                'audience_template': 'Seguidores e potenciais clientes',
                'tags': ['social', 'marketing', 'engajamento'],
                'avg_rating': 4.2,
                'usage_count': 89
            }
        ]
        
        if category:
            filtered_templates = [t for t in demo_templates if t['category'] == category]
            return filtered_templates[:limit]
        else:
            return demo_templates[:limit]
    
    def _save_template_demo(self, user_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Salva template no modo demo"""
        template_id = f"demo_template_{len(self.demo_data['templates']) + 1}"
        timestamp = datetime.now().isoformat()
        
        demo_template = {
            'id': template_id,
            'created_by': user_id,
            'title': template_data.get('titulo', 'Template sem título'),
            'description': template_data.get('descricao', ''),
            'category': template_data.get('categoria', 'geral'),
            'tags': template_data.get('tags', []),
            'created_at': timestamp,
            'avg_rating': 0.0,
            'usage_count': 0
        }
        
        self.demo_data['templates'].append(demo_template)
        
        return {
            'success': True,
            'id': template_id,
            'created_at': timestamp
        }
    
    def _log_ai_usage_demo(self, user_id: str, provider: str, tokens_used: int, cost: float) -> bool:
        """Registra uso de IA no modo demo"""
        log_entry = {
            'user_id': user_id,
            'provider': provider,
            'tokens_used': tokens_used,
            'estimated_cost': cost,
            'created_at': datetime.now().isoformat()
        }
        
        self.demo_data['ai_logs'].append(log_entry)
        return True
    
    def _get_ai_usage_stats_demo(self, user_id: str, days: int) -> Dict[str, Any]:
        """Busca estatísticas de uso de IA no modo demo"""
        # Stats simuladas para demo
        return {
            'period_days': days,
            'providers': [
                {'provider': 'groq', 'request_count': 15, 'total_tokens': 1500, 'total_cost': 0.05},
                {'provider': 'gemini', 'request_count': 8, 'total_tokens': 800, 'total_cost': 0.02}
            ],
            'total_requests': 23,
            'total_tokens': 2300,
            'total_cost': 0.07
        }

# Instância global do serviço
data_service = DataService()

# Função para obter a instância
def get_data_service() -> DataService:
    """Retorna instância global do serviço de dados"""
    return data_service