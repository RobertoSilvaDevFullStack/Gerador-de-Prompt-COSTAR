"""
Configuração do Supabase para o Gerador COSTAR
"""
import os
from typing import Optional, Dict, Any

class SupabaseConfig:
    """Configuração centralizada do Supabase"""
    
    def __init__(self):
        """Inicializa configuração com variáveis de ambiente"""
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # Configurações opcionais
        self.timeout = int(os.getenv('SUPABASE_TIMEOUT', '30'))
        self.debug = os.getenv('SUPABASE_DEBUG', 'false').lower() == 'true'
        
    def is_configured(self) -> bool:
        """Verifica se a configuração básica está presente"""
        return bool(self.url and self.anon_key)
    
    def has_admin_access(self) -> bool:
        """Verifica se tem acesso administrativo"""
        return bool(self.service_role_key)
    
    def get_public_config(self) -> Dict[str, Any]:
        """Retorna configuração para cliente público (com RLS)"""
        if not self.is_configured():
            raise ValueError("Configuração Supabase incompleta - URL e ANON_KEY necessárias")
        
        return {
            'url': self.url,
            'key': self.anon_key,
            'options': {
                'auto_refresh_token': True,
                'persist_session': True,
                'timeout': self.timeout
            }
        }
    
    def get_admin_config(self) -> Dict[str, Any]:
        """Retorna configuração para cliente admin (sem RLS)"""
        if not self.has_admin_access():
            raise ValueError("SERVICE_ROLE_KEY necessária para acesso administrativo")
        
        return {
            'url': self.url,
            'key': self.service_role_key,
            'options': {
                'auto_refresh_token': False,
                'persist_session': False,
                'timeout': self.timeout
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status da configuração"""
        return {
            'configured': self.is_configured(),
            'has_admin': self.has_admin_access(),
            'url_set': bool(self.url),
            'anon_key_set': bool(self.anon_key),
            'service_key_set': bool(self.service_role_key),
            'debug': self.debug,
            'timeout': self.timeout
        }
    
    def validate_environment(self) -> Dict[str, Any]:
        """Valida variáveis de ambiente necessárias"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificações obrigatórias
        if not self.url:
            result['valid'] = False
            result['errors'].append('SUPABASE_URL não definida')
        elif not self.url.startswith('https://'):
            result['valid'] = False
            result['errors'].append('SUPABASE_URL deve começar com https://')
        
        if not self.anon_key:
            result['valid'] = False
            result['errors'].append('SUPABASE_ANON_KEY não definida')
        elif len(self.anon_key) < 100:  # Chaves Supabase são longas
            result['warnings'].append('SUPABASE_ANON_KEY parece muito curta')
        
        # Verificações opcionais mas recomendadas
        if not self.service_role_key:
            result['warnings'].append('SUPABASE_SERVICE_ROLE_KEY não definida - funcionalidades admin limitadas')
        elif len(self.service_role_key) < 100:
            result['warnings'].append('SUPABASE_SERVICE_ROLE_KEY parece muito curta')
        
        return result

# Instância global
supabase_config = SupabaseConfig()

def get_config() -> SupabaseConfig:
    """Retorna instância global da configuração"""
    return supabase_config

def check_configuration() -> Dict[str, Any]:
    """Verifica configuração e retorna status detalhado"""
    config = get_config()
    status = config.get_status()
    validation = config.validate_environment()
    
    return {
        'status': status,
        'validation': validation,
        'ready_for_public': status['configured'] and validation['valid'],
        'ready_for_admin': status['has_admin'] and validation['valid']
    }