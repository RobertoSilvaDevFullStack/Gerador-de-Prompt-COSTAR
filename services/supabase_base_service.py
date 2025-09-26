"""
Serviço Base do Supabase - Conexão e Configuração
Responsável por estabelecer e gerenciar a conexão com o Supabase
"""

import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

class SupabaseService:
    """Serviço base para conexão com Supabase"""
    
    def __init__(self):
        """Inicializar conexão com Supabase"""
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        self.client: Optional[Client] = None
        self.admin_client: Optional[Client] = None
        
        # Verificar configurações
        if not self.url or not self.anon_key:
            logger.warning("⚠️ Supabase não configurado - usando modo demo")
            self.enabled = False
        else:
            self.enabled = True
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializar clientes Supabase"""
        try:
            # Cliente público (com RLS - Row Level Security)
            self.client = create_client(self.url, self.anon_key)
            logger.info("✅ Cliente Supabase público inicializado")
            
            # Cliente admin (sem RLS - para operações administrativas)
            if self.service_role_key:
                self.admin_client = create_client(self.url, self.service_role_key)
                logger.info("✅ Cliente Supabase admin inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Supabase: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Verificar se Supabase está habilitado e funcionando"""
        return self.enabled and self.client is not None
    
    def get_client(self, admin: bool = False) -> Optional[Client]:
        """
        Obter cliente Supabase
        
        Args:
            admin: Se True, retorna cliente admin (sem RLS)
                  Se False, retorna cliente público (com RLS)
        """
        if not self.is_enabled():
            return None
            
        if admin and self.admin_client:
            return self.admin_client
        return self.client
    
    async def test_connection(self) -> Dict[str, Any]:
        """Testar conexão com Supabase"""
        if not self.is_enabled():
            return {
                "status": "disabled",
                "message": "Supabase não configurado",
                "details": {
                    "url_configured": bool(self.url),
                    "anon_key_configured": bool(self.anon_key),
                    "service_role_configured": bool(self.service_role_key)
                }
            }
        
        try:
            # Testar com uma query simples
            result = self.client.table("_supabase_migrations").select("*").limit(1).execute()
            
            return {
                "status": "connected",
                "message": "Conexão com Supabase estabelecida com sucesso",
                "details": {
                    "url": self.url,
                    "client_initialized": bool(self.client),
                    "admin_client_initialized": bool(self.admin_client)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão Supabase: {e}")
            return {
                "status": "error",
                "message": f"Erro na conexão: {str(e)}",
                "details": {
                    "url": self.url,
                    "error_type": type(e).__name__
                }
            }
    
    def execute_query(self, table: str, operation: str, data: Dict[str, Any] = None, 
                     filters: Dict[str, Any] = None, admin: bool = False) -> Dict[str, Any]:
        """
        Executar query genérica no Supabase
        
        Args:
            table: Nome da tabela
            operation: Operação (select, insert, update, delete)
            data: Dados para insert/update
            filters: Filtros para query
            admin: Usar cliente admin (sem RLS)
        """
        if not self.is_enabled():
            return {"error": "Supabase não habilitado"}
        
        try:
            client = self.get_client(admin=admin)
            query = client.table(table)
            
            if operation == "select":
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                result = query.execute()
                
            elif operation == "insert":
                result = query.insert(data).execute()
                
            elif operation == "update":
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                result = query.update(data).execute()
                
            elif operation == "delete":
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                result = query.delete().execute()
            
            else:
                return {"error": f"Operação '{operation}' não suportada"}
            
            return {
                "success": True,
                "data": result.data,
                "count": result.count if hasattr(result, 'count') else len(result.data)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na query {operation} em {table}: {e}")
            return {
                "error": str(e),
                "operation": operation,
                "table": table
            }

# Instância global do serviço
supabase_service = SupabaseService()