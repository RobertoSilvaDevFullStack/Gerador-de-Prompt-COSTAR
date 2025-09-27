"""
Serviço de Autenticação Supabase
Integração completa com autenticação do Supabase
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import secrets
import jwt

from services.supabase_base_service import SupabaseService

logger = logging.getLogger(__name__)

# Configuração JWT
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-supabase")
JWT_ALGORITHM = "HS256"

class UserRole(Enum):
    FREE = "free"
    PRO = "pro" 
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

@dataclass
class SupabaseUser:
    id: str
    email: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @property
    def username(self) -> str:
        """Retorna username baseado no nome completo ou email"""
        if self.full_name:
            return self.full_name
        return self.email.split('@')[0]
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url
        }

class SupabaseAuthService(SupabaseService):
    """Serviço de autenticação usando Supabase"""
    
    def __init__(self):
        super().__init__()
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 24
    
    def register_user(self, email: str, password: str, username: str = None, role: UserRole = UserRole.FREE) -> Optional[SupabaseUser]:
        """Registrar novo usuário (método simplificado)"""
        if not self.enabled:
            return None
        
        try:
            # Verificar se email já existe
            existing = self.get_user_by_email(email)
            if existing:
                logger.error(f"Email {email} já está em uso")
                return None
            
            # Gerar ID e hash da senha
            user_id = self._generate_user_id()
            password_hash = self._hash_password(password)
            display_name = username or email.split('@')[0]
            
            # Criar dados do usuário
            profile_data = {
                "id": user_id,
                "email": email,
                "username": display_name,
                "password_hash": password_hash,
                "full_name": display_name,
                "role": role.value,
                "is_active": True,
                "preferences": {
                    "default_style": "Profissional",
                    "default_tone": "Formal"
                }
            }
            
            # Inserir no banco
            result = self.admin_client.table("costar_users").insert(profile_data).execute()
            
            if result.data:
                logger.info(f"✅ Usuário registrado: {email}")
                return self._row_to_user(result.data[0])
            else:
                logger.error(f"❌ Erro ao criar perfil para {email}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar usuário {email}: {str(e)}")
            return None
    
    def create_admin_user(self, email: str, password: str, full_name: str = "Administrator") -> Optional[SupabaseUser]:
        """Criar usuário administrador"""
        if not self.enabled:
            logger.error("Supabase não está configurado")
            return None
        
        try:
            # Verificar se usuário já existe
            existing = self.admin_client.table("costar_users").select("*").eq("email", email).execute()
            if existing.data:
                logger.info(f"Usuário admin {email} já existe")
                return self._row_to_user(existing.data[0])
            
            # Criar usuário no Supabase Auth (simulado via user_profiles)
            user_id = self._generate_user_id()
            password_hash = self._hash_password(password)
            
            user_data = {
                "id": user_id,
                "email": email,
                "username": email.split('@')[0] + "_admin",
                "password_hash": password_hash,
                "full_name": full_name,
                "role": "admin",
                "is_active": True,
                "preferences": {
                    "permissions": ["manage_users", "manage_content", "view_analytics"],
                    "api_calls_limit": 10000
                }
            }
            
            result = self.admin_client.table("costar_users").insert(user_data).execute()
            
            if result.data:
                logger.info(f"✅ Usuário admin criado: {email}")
                return self._row_to_user(result.data[0])
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
        
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Autenticar usuário e retornar JWT token"""
        if not self.enabled:
            return None
        
        try:
            # Buscar usuário por email
            result = self.admin_client.table("costar_users").select("*").eq("email", email).execute()
            
            if not result.data:
                logger.warning(f"Usuário não encontrado: {email}")
                return None
                
            user_data = result.data[0]
            
            if not user_data:
                logger.warning(f"Usuário não encontrado: {email}")
                return None
            
            # Verificar senha
            stored_hash = user_data.get('password_hash')
            if not stored_hash:
                logger.warning(f"Hash de senha não encontrado para: {email}")
                return None
                
            if not self._verify_password(password, stored_hash):
                logger.warning(f"Senha inválida para: {email}")
                return None
            
            # Atualizar último login
            self.admin_client.table("costar_users").update({
                "last_login": datetime.now().isoformat()
            }).eq("id", user_data['id']).execute()
            
            # Gerar JWT token
            token_payload = {
                "user_id": user_data['id'],
                "email": email,
                "role": user_data.get('role', 'free'),
                "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours)
            }
            
            token = jwt.encode(token_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            logger.info(f"✅ Login realizado: {email}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[SupabaseUser]:
        """Buscar usuário por ID"""
        if not self.enabled:
            return None
        
        try:
            result = self.admin_client.table("costar_users").select("*").eq("id", user_id).execute()
            
            if result.data:
                return self._row_to_user(result.data[0])
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuário por ID: {e}")
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[SupabaseUser]:
        """Buscar usuário por email"""
        if not self.enabled:
            return None
        
        try:
            result = self.admin_client.table("costar_users").select("*").eq("email", email).execute()
            
            if result.data:
                return self._row_to_user(result.data[0])
                    
        except Exception as e:
            logger.error(f"❌ Erro ao buscar usuário por email: {e}")
        
        return None
    
    def get_all_users(self) -> List[Dict]:
        """Obter todos os usuários"""
        if not self.enabled:
            return []
        
        try:
            result = self.admin_client.table("costar_users").select("*").execute()
            
            users = []
            for row in result.data:
                user = self._row_to_user(row)
                if user:
                    users.append(user.to_dict())
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar todos os usuários: {e}")
            return []
    
    def verify_token(self, token: str) -> Optional[SupabaseUser]:
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            
            if not user_id:
                return None
            
            return self.get_user_by_id(user_id)
            
        except jwt.InvalidTokenError:
            logger.error("Token JWT inválido")
            return None
        except Exception as e:
            logger.error(f"Erro ao verificar token: {str(e)}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """Deletar usuário (para testes)"""
        if not self.enabled:
            return False
        
        try:
            # Deletar do perfil
            result = self.admin_client.table("costar_users").delete().eq("id", user_id).execute()
            
            # Deletar do auth (se possível)
            try:
                self.admin_client.auth.admin.delete_user(user_id)
            except:
                pass  # Pode falhar se usuário não existir no auth
            
            logger.info(f"✅ Usuário {user_id} deletado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao deletar usuário {user_id}: {str(e)}")
            return False
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Atualizar dados do usuário"""
        if not self.enabled:
            return False
        
        try:
            # Mapear campos para a estrutura do Supabase
            supabase_updates = {}
            
            if 'is_active' in updates:
                # No Supabase, ativo/inativo pode ser controlado via subscription_status
                supabase_updates['subscription_status'] = 'active' if updates['is_active'] else 'inactive'
            
            if 'full_name' in updates:
                supabase_updates['full_name'] = updates['full_name']
            
            if supabase_updates:
                supabase_updates['updated_at'] = datetime.now().isoformat()
                result = self.admin_client.table("costar_users").update(supabase_updates).eq("id", user_id).execute()
                return len(result.data) > 0
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar usuário: {e}")
            return False
    
    def _row_to_user(self, row: Dict) -> Optional[SupabaseUser]:
        """Converter linha do Supabase para objeto User"""
        try:
            # Mapear role para UserRole
            role_mapping = {
                'free': UserRole.FREE,
                'pro': UserRole.PRO,
                'enterprise': UserRole.ENTERPRISE,
                'admin': UserRole.ADMIN
            }
            
            role = role_mapping.get(row.get('role', 'free'), UserRole.FREE)
            
            return SupabaseUser(
                id=row['id'],
                email=row.get('email', f"user_{row['id'][:8]}@system.local"),
                role=role,
                created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                last_login=datetime.fromisoformat(row['last_login'].replace('Z', '+00:00')) if row.get('last_login') else None,
                is_active=row.get('is_active', True),
                full_name=row.get('full_name'),
                avatar_url=row.get('avatar_url')
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao converter linha para usuário: {e}")
            return None
    
    def _generate_user_id(self) -> str:
        """Gerar ID único para usuário"""
        import uuid
        return str(uuid.uuid4())
    
    def _hash_password(self, password: str) -> str:
        """Hash da senha usando SHA-256 com salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{pwd_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verificar senha"""
        try:
            if ':' not in stored_hash:
                # Hash antigo sem salt - compatibilidade
                return hashlib.sha256(password.encode()).hexdigest() == stored_hash
            
            salt, pwd_hash = stored_hash.split(':', 1)
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
            
        except Exception:
            return False
    
    def update_user_password(self, user_id: str, new_password: str) -> bool:
        """Atualizar senha do usuário"""
        if not self.enabled:
            return False
        
        try:
            # Hash da nova senha
            password_hash = self._hash_password(new_password)
            
            # Atualizar no Supabase
            result = self.admin_client.table("costar_users").update({
                "password_hash": password_hash,
                "updated_at": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            success = len(result.data) > 0
            
            if success:
                logger.info(f"✅ Senha atualizada para usuário {user_id}")
            else:
                logger.error(f"❌ Falha ao atualizar senha para usuário {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar senha: {e}")
            return False