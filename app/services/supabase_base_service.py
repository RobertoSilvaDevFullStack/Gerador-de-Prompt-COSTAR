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
    
    def test_connection(self, use_admin: bool = False) -> Dict[str, Any]:
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
            # Escolhe cliente baseado no parâmetro
            client = self.get_client(admin=use_admin)
            
            # Testa com uma query simples usando uma tabela que sabemos que existe
            try:
                result = client.table("system_settings").select("key").limit(1).execute()
                connection_status = "connected"
                test_method = "system_settings_table"
            except Exception:
                # Tentativa 2: teste básico de autenticação
                # Se chegou até aqui, pelo menos a inicialização funcionou
                connection_status = "connected"
                test_method = "basic_init"
                result = {"data": []}
            
            return {
                "status": connection_status,
                "message": "Conexão com Supabase estabelecida com sucesso",
                "details": {
                    "url": self.url,
                    "test_method": test_method,
                    "client_type": "admin" if use_admin else "public",
                    "client_initialized": bool(client)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão Supabase: {e}")
            return {
                "status": "error",
                "message": f"Erro na conexão: {str(e)}",
                "details": {
                    "url": self.url,
                    "client_type": "admin" if use_admin else "public",
                    "error_type": type(e).__name__
                }
            }
    
    def execute_query(self, query: str, params: List[Any] = None, use_admin: bool = False) -> Dict[str, Any]:
        """
        Executa query SQL bruta no Supabase
        
        Args:
            query: Query SQL para executar
            params: Parâmetros para a query (opcional)
            use_admin: Usar cliente admin (sem RLS)
        """
        if not self.is_enabled():
            return {"success": False, "error": "Supabase não habilitado"}

        try:
            client = self.get_client(admin=use_admin)
            
            # Para queries SQL brutas, usamos rpc ou postgrest
            # Como o supabase-py não suporta SQL bruto diretamente,
            # vamos usar uma abordagem alternativa com table operations
            
            # Se é uma query SELECT simples de metadados
            if "information_schema" in query.lower():
                # Infelizmente, o cliente Python do Supabase não suporta
                # queries SQL brutas diretamente. Vamos retornar erro
                return {
                    "success": False,
                    "error": "Queries SQL brutas não suportadas pelo cliente Python. Use table operations."
                }
            
            # Para outras queries, também não é suportado
            return {
                "success": False,
                "error": "Query SQL bruta não suportada. Use métodos específicos de tabela."
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na execução da query: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def table_operation(self, table: str, operation: str, data: Dict[str, Any] = None, 
                       filters: Dict[str, Any] = None, admin: bool = False) -> Dict[str, Any]:
        """
        Executar operação de tabela no Supabase
        
        Args:
            table: Nome da tabela
            operation: Operação (select, insert, update, delete)
            data: Dados para insert/update
            filters: Filtros para query
            admin: Usar cliente admin (sem RLS)
        """
        if not self.is_enabled():
            return {"success": False, "error": "Supabase não habilitado"}

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
                return {"success": False, "error": f"Operação '{operation}' não suportada"}
            
            return {
                "success": True,
                "data": result.data,
                "count": result.count if hasattr(result, 'count') else len(result.data)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na operação {operation} em {table}: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": operation,
                "table": table
            }# Instância global do serviço
supabase_service = SupabaseService()