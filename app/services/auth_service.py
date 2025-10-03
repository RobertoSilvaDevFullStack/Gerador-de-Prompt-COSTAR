"""
Sistema de Autenticação e Gerenciamento de Usuários
"""
import hashlib
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    FREE = "free"

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    profile: Optional[Dict] = None
    
    @property
    def username(self) -> str:
        """Retorna username baseado no email ou nome do perfil"""
        if self.profile and self.profile.get('name'):
            return self.profile['name']
        return self.email.split('@')[0]  # Usa a parte antes do @ como username
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'profile': self.profile or {}
        }

@dataclass
class SavedPrompt:
    id: str
    user_id: str
    title: str
    contexto: str
    objetivo: str
    estilo: str
    tom: str
    audiencia: str
    resposta: str
    generated_prompt: str
    created_at: datetime
    is_public: bool = False
    tags: Optional[List[str]] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class UserSession:
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
        self.users_file = 'data/users.json'
        self.sessions_file = 'data/sessions.json'
        self.saved_prompts_file = 'data/saved_prompts.json'
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Criar diretório de dados se não existir"""
        os.makedirs('data', exist_ok=True)
        
        # Criar arquivos vazios se não existirem
        for file_path in [self.users_file, self.sessions_file, self.saved_prompts_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def _hash_password(self, password: str) -> str:
        """Hash da senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar senha"""
        return self._hash_password(password) == password_hash
    
    def _generate_jwt_token(self, user_id: str, role: UserRole) -> str:
        """Gerar token JWT"""
        payload = {
            'user_id': user_id,
            'role': role.value,
            'exp': datetime.utcnow() + timedelta(days=7),  # Token válido por 7 dias
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, email: str, password: str, role: UserRole = UserRole.FREE) -> Optional[User]:
        """Registrar novo usuário"""
        # Verificar se email já existe
        if self.get_user_by_email(email):
            return None
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=self._hash_password(password),
            role=role,
            created_at=datetime.now(),
            profile={
                'name': '',
                'company': '',
                'preferences': {
                    'default_style': 'Profissional',
                    'default_tone': 'Formal',
                    'favorite_use_cases': []
                }
            }
        )
        
        # Salvar usuário
        users = self._load_users()
        users[user.id] = user.to_dict()
        self._save_users(users)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Autenticar usuário e retornar token JWT"""
        user = self.get_user_by_email(email)
        if not user or not self._verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        # Atualizar último login
        user.last_login = datetime.now()
        self.update_user(user.id, {"last_login": user.last_login.isoformat()})
        
        return self._generate_jwt_token(user.id, user.role)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        users = self._load_users()
        for user_data in users.values():
            if user_data['email'] == email:
                return self._dict_to_user(user_data)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Buscar usuário por ID"""
        users = self._load_users()
        user_data = users.get(user_id)
        return self._dict_to_user(user_data) if user_data else None
    

    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Obter usuário a partir do token JWT"""
        payload = self._verify_jwt_token(token)
        if not payload:
            return None
        
        return self.get_user_by_id(payload['user_id'])
    
    def save_prompt(self, user_id: str, prompt_data: Dict, generated_prompt: str) -> SavedPrompt:
        """Salvar prompt do usuário"""
        saved_prompt = SavedPrompt(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=f"Prompt {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            contexto=prompt_data.get('contexto', ''),
            objetivo=prompt_data.get('objetivo', ''),
            estilo=prompt_data.get('estilo', ''),
            tom=prompt_data.get('tom', ''),
            audiencia=prompt_data.get('audiencia', ''),
            resposta=prompt_data.get('resposta', ''),
            generated_prompt=generated_prompt,
            created_at=datetime.now(),
            tags=prompt_data.get('tags', [])
        )
        
        # Salvar no arquivo
        prompts = self._load_saved_prompts()
        prompts[saved_prompt.id] = saved_prompt.to_dict()
        self._save_saved_prompts(prompts)
        
        return saved_prompt
    
    def get_user_prompts(self, user_id: str) -> List[SavedPrompt]:
        """Obter prompts salvos do usuário"""
        prompts = self._load_saved_prompts()
        user_prompts = []
        
        for prompt_data in prompts.values():
            if prompt_data['user_id'] == user_id:
                user_prompts.append(self._dict_to_saved_prompt(prompt_data))
        
        return sorted(user_prompts, key=lambda x: x.created_at, reverse=True)
    
    def delete_prompt(self, user_id: str, prompt_id: str) -> bool:
        """Deletar prompt do usuário"""
        prompts = self._load_saved_prompts()
        if prompt_id in prompts and prompts[prompt_id]['user_id'] == user_id:
            del prompts[prompt_id]
            self._save_saved_prompts(prompts)
            return True
        return False
    
    def _load_users(self) -> Dict:
        """Carregar usuários do arquivo"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict):
        """Salvar usuários no arquivo"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    def _load_saved_prompts(self) -> Dict:
        """Carregar prompts salvos"""
        try:
            with open(self.saved_prompts_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_saved_prompts(self, prompts: Dict):
        """Salvar prompts"""
        with open(self.saved_prompts_file, 'w') as f:
            json.dump(prompts, f, indent=2, default=str)
    
    def _dict_to_user(self, data: Dict) -> User:
        """Converter dict para User"""
        return User(
            id=data['id'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=UserRole(data['role']),
            created_at=datetime.fromisoformat(data['created_at']),
            last_login=datetime.fromisoformat(data['last_login']) if data.get('last_login') else None,
            is_active=data.get('is_active', True),
            profile=data.get('profile', {})
        )
    
    def _dict_to_saved_prompt(self, data: Dict) -> SavedPrompt:
        """Converter dict para SavedPrompt"""
        return SavedPrompt(
            id=data['id'],
            user_id=data['user_id'],
            title=data['title'],
            contexto=data['contexto'],
            objetivo=data['objetivo'],
            estilo=data['estilo'],
            tom=data['tom'],
            audiencia=data['audiencia'],
            resposta=data['resposta'],
            generated_prompt=data['generated_prompt'],
            created_at=datetime.fromisoformat(data['created_at']),
            is_public=data.get('is_public', False),
            tags=data.get('tags', [])
        )
    
    def get_all_users(self) -> List[Dict]:
        """Obter todos os usuários"""
        users = self._load_users()
        return list(users.values())
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Atualizar dados do usuário"""
        users = self._load_users()
        if user_id in users:
            users[user_id].update(updates)
            self._save_users(users)
            return True
        return False