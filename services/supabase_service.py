from supabase import create_client, Client
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
import json

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Client = create_client(self.url, self.key)
    
    async def create_user(self, email: str, password: str, metadata: Dict[str, Any] | None = None):
        """Criar novo usuário"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "metadata": response.user.user_metadata
                }
            else:
                raise Exception("Falha na criação do usuário")
                
        except Exception as e:
            raise Exception(f"Erro ao criar usuário: {str(e)}")
    
    async def login_user(self, email: str, password: str):
        """Login de usuário"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            return {
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "metadata": response.user.user_metadata
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            }
        except Exception as e:
            raise Exception(f"Erro no login: {str(e)}")
    
    async def logout_user(self):
        """Logout de usuário"""
        try:
            self.client.auth.sign_out()
        except Exception as e:
            raise Exception(f"Erro no logout: {str(e)}")
    
    async def verify_token(self, token: str):
        """Verificar token JWT"""
        try:
            user = self.client.auth.get_user(token)
            if user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "metadata": user.user.user_metadata
                }
            return None
        except Exception as e:
            return None
    
    async def create_prompt(
        self,
        user_id: str,
        titulo: str,
        prompt_data: Dict[str, Any],
        prompt_completo: str,
        categoria: str = "geral",
        tags: List[str] = None,
        favorito: bool = False,
        compartilhado: bool = False
    ):
        """Criar novo prompt"""
        try:
            data = {
                "titulo": titulo,
                "contexto": prompt_data.get("contexto"),
                "objetivo": prompt_data.get("objetivo"),
                "estilo": prompt_data.get("estilo"),
                "tom": prompt_data.get("tom"),
                "audiencia": prompt_data.get("audiencia"),
                "resposta": prompt_data.get("resposta"),
                "prompt_completo": prompt_completo,
                "usuario_id": user_id,
                "categoria": categoria,
                "tags": tags or [],
                "favorito": favorito,
                "compartilhado": compartilhado,
                "criado_em": datetime.now().isoformat(),
                "atualizado_em": datetime.now().isoformat()
            }
            
            response = self.client.table("prompts").insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            raise Exception(f"Erro ao criar prompt: {str(e)}")
    
    async def get_prompts(
        self,
        user_id: str,
        categoria: Optional[str] = None,
        favorito: Optional[bool] = None,
        busca: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ):
        """Buscar prompts do usuário"""
        try:
            query = self.client.table("prompts").select("*").eq("usuario_id", user_id)
            
            if categoria:
                query = query.eq("categoria", categoria)
            
            if favorito is not None:
                query = query.eq("favorito", favorito)
            
            if busca:
                query = query.or_(f"titulo.ilike.%{busca}%,contexto.ilike.%{busca}%")
            
            # Paginação
            start = (page - 1) * limit
            end = start + limit - 1
            
            query = query.order("criado_em", desc=True).range(start, end)
            
            response = query.execute()
            return {
                "data": response.data,
                "page": page,
                "limit": limit,
                "total": len(response.data)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao buscar prompts: {str(e)}")
    
    async def get_prompt(self, prompt_id: str, user_id: str):
        """Buscar prompt específico"""
        try:
            response = self.client.table("prompts").select("*").eq("id", prompt_id).eq("usuario_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Erro ao buscar prompt: {str(e)}")
    
    async def update_prompt(self, prompt_id: str, user_id: str, update_data: Dict[str, Any]):
        """Atualizar prompt"""
        try:
            update_data["atualizado_em"] = datetime.now().isoformat()
            
            response = self.client.table("prompts").update(update_data).eq("id", prompt_id).eq("usuario_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Erro ao atualizar prompt: {str(e)}")
    
    async def delete_prompt(self, prompt_id: str, user_id: str):
        """Excluir prompt"""
        try:
            self.client.table("prompts").delete().eq("id", prompt_id).eq("usuario_id", user_id).execute()
        except Exception as e:
            raise Exception(f"Erro ao excluir prompt: {str(e)}")
    
    async def get_templates(self, categoria: Optional[str] = None):
        """Buscar templates públicos"""
        try:
            query = self.client.table("templates").select("*").eq("publico", True)
            
            if categoria:
                query = query.eq("categoria", categoria)
            
            response = query.order("usos", desc=True).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Erro ao buscar templates: {str(e)}")
    
    async def create_template(
        self,
        user_id: str,
        nome: str,
        descricao: str,
        prompt_data: Dict[str, Any],
        categoria: str,
        publico: bool = True
    ):
        """Criar novo template"""
        try:
            data = {
                "nome": nome,
                "descricao": descricao,
                "contexto": prompt_data.get("contexto"),
                "objetivo": prompt_data.get("objetivo"),
                "estilo": prompt_data.get("estilo"),
                "tom": prompt_data.get("tom"),
                "audiencia": prompt_data.get("audiencia"),
                "resposta": prompt_data.get("resposta"),
                "categoria": categoria,
                "publico": publico,
                "usuario_criador": user_id,
                "usos": 0,
                "criado_em": datetime.now().isoformat(),
                "atualizado_em": datetime.now().isoformat()
            }
            
            response = self.client.table("templates").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Erro ao criar template: {str(e)}")
    
    async def get_all_user_prompts(self, user_id: str):
        """Buscar todos os prompts do usuário para export"""
        try:
            response = self.client.table("prompts").select("*").eq("usuario_id", user_id).order("criado_em", desc=True).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Erro ao buscar prompts para export: {str(e)}")
