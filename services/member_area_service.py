"""
Sistema de Área de Membros - Interface para usuários premium
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid
from enum import Enum

class SubscriptionPlan(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class UserProfile:
    user_id: str
    username: str
    email: str
    subscription_plan: SubscriptionPlan
    created_at: datetime
    last_login: datetime
    preferences: Dict[str, Any]
    usage_stats: Dict[str, int]
    custom_templates: List[str]
    api_quota: Dict[str, int]
    usage_current_month: Dict[str, int]

@dataclass
class SavedPromptTemplate:
    id: str
    user_id: str
    name: str
    description: str
    category: str
    template_content: Dict[str, str]  # Context, Task, Style, Tone, Audience, Response
    is_public: bool
    created_at: datetime
    updated_at: datetime
    usage_count: int
    tags: List[str]
    rating: float
    votes: int

@dataclass
class MemberAnalytics:
    user_id: str
    total_prompts_generated: int
    prompts_this_month: int
    favorite_categories: List[str]
    most_used_providers: List[str]
    avg_prompt_quality_score: float
    saved_templates_count: int
    shared_templates_count: int
    member_since: datetime
    subscription_renewal_date: Optional[datetime]

class MemberAreaService:
    def __init__(self):
        self.users_file = 'data/member_profiles.json'
        self.templates_file = 'data/saved_templates.json'
        self.analytics_file = 'data/member_analytics.json'
        self._ensure_member_data_files()
        
        # Configurações de quota por plano
        self.plan_quotas = {
            SubscriptionPlan.FREE: {
                'monthly_prompts': 50,
                'saved_templates': 5,
                'api_providers': ['gemini'],
                'advanced_features': False
            },
            SubscriptionPlan.PREMIUM: {
                'monthly_prompts': 500,
                'saved_templates': 50,
                'api_providers': ['gemini', 'groq', 'huggingface', 'cohere'],
                'advanced_features': True
            },
            SubscriptionPlan.ENTERPRISE: {
                'monthly_prompts': -1,  # Ilimitado
                'saved_templates': -1,  # Ilimitado
                'api_providers': ['all'],
                'advanced_features': True
            }
        }
    
    def _ensure_member_data_files(self):
        """Criar arquivos de dados de membros se não existirem"""
        os.makedirs('data', exist_ok=True)
        
        for file_path in [self.users_file, self.templates_file, self.analytics_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def create_member_profile(self, user_id: str, username: str, email: str, 
                            subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE) -> UserProfile:
        """Criar perfil de membro"""
        profile = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            subscription_plan=subscription_plan,
            created_at=datetime.now(),
            last_login=datetime.now(),
            preferences={
                'default_style': 'professional',
                'default_tone': 'neutral',
                'preferred_providers': ['gemini'],
                'auto_save_prompts': True,
                'email_notifications': True,
                'theme': 'light'
            },
            usage_stats={
                'total_prompts': 0,
                'templates_created': 0,
                'templates_shared': 0
            },
            custom_templates=[],
            api_quota=self.plan_quotas[subscription_plan],
            usage_current_month={
                'prompts_generated': 0,
                'api_calls': 0,
                'tokens_used': 0
            }
        )
        
        # Salvar perfil
        profiles = self._load_member_profiles()
        profiles.append(asdict(profile))
        self._save_member_profiles(profiles)
        
        return profile
    
    def get_member_profile(self, user_id: str) -> Optional[UserProfile]:
        """Obter perfil do membro"""
        profiles = self._load_member_profiles()
        for profile_data in profiles:
            if profile_data['user_id'] == user_id:
                # Corrige conversão do enum - remove SubscriptionPlan. se presente
                plan_value = profile_data['subscription_plan']
                if isinstance(plan_value, str) and plan_value.startswith('SubscriptionPlan.'):
                    plan_value = plan_value.replace('SubscriptionPlan.', '').lower()
                profile_data['subscription_plan'] = SubscriptionPlan(plan_value)
                profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
                profile_data['last_login'] = datetime.fromisoformat(profile_data['last_login'])
                
                # Adicionar campos obrigatórios se não existirem
                if 'custom_templates' not in profile_data:
                    profile_data['custom_templates'] = []
                if 'api_quota' not in profile_data:
                    # Obter quota baseada no plano
                    plan_quota = self.plan_quotas[profile_data['subscription_plan']]
                    profile_data['api_quota'] = {
                        'monthly_prompts': plan_quota['monthly_prompts'],
                        'saved_templates': plan_quota['saved_templates'],
                        'api_providers': plan_quota['api_providers'],
                        'advanced_features': plan_quota['advanced_features']
                    }
                
                return UserProfile(**profile_data)
        return None
    
    def update_member_profile(self, user_id: str, updates: Dict) -> bool:
        """Atualizar perfil do membro"""
        profiles = self._load_member_profiles()
        for i, profile in enumerate(profiles):
            if profile['user_id'] == user_id:
                profile.update(updates)
                profiles[i] = profile
                self._save_member_profiles(profiles)
                return True
        return False
    
    def create_prompt_template(self, user_id: str, name: str, description: str, 
                             category: str, template_content: Dict[str, str],
                             is_public: bool = False, tags: Optional[List[str]] = None) -> SavedPromptTemplate:
        """Criar template de prompt personalizado"""
        template = SavedPromptTemplate(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            description=description,
            category=category,
            template_content=template_content,
            is_public=is_public,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            usage_count=0,
            tags=tags or [],
            rating=0.0,
            votes=0
        )
        
        # Verificar quota
        profile = self.get_member_profile(user_id)
        if profile:
            quota = self.plan_quotas[profile.subscription_plan]['saved_templates']
            if quota != -1:  # Se não é ilimitado
                user_templates = self.get_user_templates(user_id)
                if len(user_templates) >= quota:
                    raise Exception(f"Quota de templates excedida. Plano {profile.subscription_plan.value} permite apenas {quota} templates.")
        
        # Salvar template
        templates = self._load_templates()
        templates.append(asdict(template))
        self._save_templates(templates)
        
        # Atualizar estatísticas do usuário
        self.update_member_usage_stats(user_id, 'templates_created', 1)
        
        return template
    
    def get_user_templates(self, user_id: str) -> List[SavedPromptTemplate]:
        """Obter templates do usuário"""
        templates = self._load_templates()
        user_templates = []
        
        for template_data in templates:
            if template_data['user_id'] == user_id:
                template_data['created_at'] = datetime.fromisoformat(template_data['created_at'])
                template_data['updated_at'] = datetime.fromisoformat(template_data['updated_at'])
                user_templates.append(SavedPromptTemplate(**template_data))
        
        return user_templates
    
    def get_public_templates(self, category: Optional[str] = None, 
                           search_term: Optional[str] = None) -> List[SavedPromptTemplate]:
        """Obter templates públicos"""
        templates = self._load_templates()
        public_templates = []
        
        for template_data in templates:
            if template_data['is_public']:
                # Filtrar por categoria se especificada
                if category and template_data['category'] != category:
                    continue
                
                # Filtrar por termo de busca se especificado
                if search_term:
                    search_term_lower = search_term.lower()
                    if (search_term_lower not in template_data['name'].lower() and
                        search_term_lower not in template_data['description'].lower() and
                        not any(search_term_lower in tag.lower() for tag in template_data['tags'])):
                        continue
                
                template_data['created_at'] = datetime.fromisoformat(template_data['created_at'])
                template_data['updated_at'] = datetime.fromisoformat(template_data['updated_at'])
                public_templates.append(SavedPromptTemplate(**template_data))
        
        # Ordenar por rating e número de usos
        public_templates.sort(key=lambda t: (t.rating, t.usage_count), reverse=True)
        return public_templates
    
    def use_template(self, template_id: str, user_id: str) -> Optional[SavedPromptTemplate]:
        """Usar um template (incrementa contador de uso)"""
        templates = self._load_templates()
        
        for i, template_data in enumerate(templates):
            if template_data['id'] == template_id:
                template_data['usage_count'] += 1
                templates[i] = template_data
                self._save_templates(templates)
                
                # Atualizar estatísticas do usuário
                self.update_member_usage_stats(user_id, 'total_prompts', 1)
                
                template_data['created_at'] = datetime.fromisoformat(template_data['created_at'])
                template_data['updated_at'] = datetime.fromisoformat(template_data['updated_at'])
                return SavedPromptTemplate(**template_data)
        
        return None
    
    def rate_template(self, template_id: str, user_id: str, rating: float) -> bool:
        """Avaliar template (rating de 1 a 5)"""
        if not 1 <= rating <= 5:
            return False
        
        templates = self._load_templates()
        
        for i, template_data in enumerate(templates):
            if template_data['id'] == template_id:
                # Calcular nova média de rating
                current_rating = template_data['rating']
                current_votes = template_data['votes']
                
                new_votes = current_votes + 1
                new_rating = ((current_rating * current_votes) + rating) / new_votes
                
                template_data['rating'] = round(new_rating, 2)
                template_data['votes'] = new_votes
                
                templates[i] = template_data
                self._save_templates(templates)
                return True
        
        return False
    
    def get_member_analytics(self, user_id: str) -> Optional[MemberAnalytics]:
        """Obter analytics do membro"""
        profile = self.get_member_profile(user_id)
        if not profile:
            return None
        
        user_templates = self.get_user_templates(user_id)
        public_templates = [t for t in user_templates if t.is_public]
        
        # Calcular estatísticas avançadas
        total_usage = sum(t.usage_count for t in user_templates)
        avg_rating = sum(t.rating for t in public_templates if t.votes > 0) / len(public_templates) if public_templates else 0
        
        analytics = MemberAnalytics(
            user_id=user_id,
            total_prompts_generated=profile.usage_stats.get('total_prompts', 0),
            prompts_this_month=profile.usage_current_month.get('prompts_generated', 0),
            favorite_categories=self._get_favorite_categories(user_id),
            most_used_providers=profile.preferences.get('preferred_providers', []),
            avg_prompt_quality_score=avg_rating,
            saved_templates_count=len(user_templates),
            shared_templates_count=len(public_templates),
            member_since=profile.created_at,
            subscription_renewal_date=self._calculate_renewal_date(profile)
        )
        
        return analytics
    
    def check_usage_quota(self, user_id: str, quota_type: str) -> Dict[str, Any]:
        """Verificar quota de uso"""
        profile = self.get_member_profile(user_id)
        if not profile:
            return {'allowed': False, 'reason': 'Usuário não encontrado'}
        
        quota_limits = self.plan_quotas[profile.subscription_plan]
        current_usage = profile.usage_current_month
        
        if quota_type == 'prompts':
            limit = quota_limits['monthly_prompts']
            used = current_usage.get('prompts_generated', 0)
            
            if limit == -1:  # Ilimitado
                return {'allowed': True, 'remaining': -1, 'limit': -1}
            
            remaining = max(0, limit - used)
            return {
                'allowed': remaining > 0,
                'remaining': remaining,
                'limit': limit,
                'used': used,
                'percentage': (used / limit * 100) if limit > 0 else 0
            }
        
        elif quota_type == 'templates':
            limit = quota_limits['saved_templates']
            user_templates = self.get_user_templates(user_id)
            used = len(user_templates)
            
            if limit == -1:  # Ilimitado
                return {'allowed': True, 'remaining': -1, 'limit': -1}
            
            remaining = max(0, limit - used)
            return {
                'allowed': remaining > 0,
                'remaining': remaining,
                'limit': limit,
                'used': used,
                'percentage': (used / limit * 100) if limit > 0 else 0
            }
        
        return {'allowed': False, 'reason': 'Tipo de quota inválido'}
    
    def update_member_usage_stats(self, user_id: str, stat_type: str, increment: int = 1):
        """Atualizar estatísticas de uso do membro"""
        profiles = self._load_member_profiles()
        
        for i, profile in enumerate(profiles):
            if profile['user_id'] == user_id:
                # Atualizar estatísticas totais
                if stat_type in profile['usage_stats']:
                    profile['usage_stats'][stat_type] += increment
                else:
                    profile['usage_stats'][stat_type] = increment
                
                # Atualizar uso do mês atual para prompts
                if stat_type == 'total_prompts':
                    if 'prompts_generated' in profile['usage_current_month']:
                        profile['usage_current_month']['prompts_generated'] += increment
                    else:
                        profile['usage_current_month']['prompts_generated'] = increment
                
                profiles[i] = profile
                self._save_member_profiles(profiles)
                break
    
    def upgrade_subscription(self, user_id: str, new_plan: SubscriptionPlan) -> bool:
        """Fazer upgrade da assinatura"""
        updates = {
            'subscription_plan': new_plan.value,
            'api_quota': self.plan_quotas[new_plan]
        }
        return self.update_member_profile(user_id, updates)
    
    def _get_favorite_categories(self, user_id: str) -> List[str]:
        """Obter categorias favoritas baseadas no uso"""
        templates = self.get_user_templates(user_id)
        category_usage = {}
        
        for template in templates:
            category = template.category
            category_usage[category] = category_usage.get(category, 0) + template.usage_count
        
        # Retornar top 3 categorias
        sorted_categories = sorted(category_usage.items(), key=lambda x: x[1], reverse=True)
        return [cat[0] for cat in sorted_categories[:3]]
    
    def _calculate_renewal_date(self, profile: UserProfile) -> Optional[datetime]:
        """Calcular data de renovação da assinatura"""
        if profile.subscription_plan == SubscriptionPlan.FREE:
            return None
        
        # Assumir ciclo mensal
        return profile.created_at + timedelta(days=30)
    
    def _load_member_profiles(self) -> List:
        """Carregar perfis de membros"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_member_profiles(self, profiles: List):
        """Salvar perfis de membros"""
        with open(self.users_file, 'w') as f:
            json.dump(profiles, f, indent=2, default=str)
    
    def _load_templates(self) -> List:
        """Carregar templates salvos"""
        try:
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_templates(self, templates: List):
        """Salvar templates"""
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2, default=str)
    
    def create_subscription(self, user_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Criar nova assinatura"""
        try:
            # Carregar dados existentes
            subscriptions_file = os.path.join("data", "subscriptions.json")
            subscriptions = []
            
            if os.path.exists(subscriptions_file):
                try:
                    with open(subscriptions_file, 'r') as f:
                        subscriptions = json.load(f)
                except json.JSONDecodeError:
                    subscriptions = []
            
            # Adicionar nova assinatura
            subscription_data['id'] = str(uuid.uuid4())
            subscriptions.append(subscription_data)
            
            # Salvar
            with open(subscriptions_file, 'w') as f:
                json.dump(subscriptions, f, indent=2, default=str)
            
            # Atualizar perfil do usuário
            plan_map = {
                "premium": SubscriptionPlan.PREMIUM,
                "enterprise": SubscriptionPlan.ENTERPRISE
            }
            
            new_plan = plan_map.get(subscription_data.get("plan"), SubscriptionPlan.FREE)
            self.upgrade_subscription(user_id, new_plan)
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar assinatura: {e}")
            return False
    
    def cancel_subscription(self, user_id: str) -> bool:
        """Cancelar assinatura"""
        try:
            # Carregar assinaturas
            subscriptions_file = os.path.join("data", "subscriptions.json")
            subscriptions = []
            
            if os.path.exists(subscriptions_file):
                try:
                    with open(subscriptions_file, 'r') as f:
                        subscriptions = json.load(f)
                except json.JSONDecodeError:
                    subscriptions = []
            
            # Encontrar e cancelar assinatura do usuário
            for subscription in subscriptions:
                if subscription.get("user_id") == user_id:
                    subscription["status"] = "cancelled"
                    subscription["cancelled_at"] = datetime.now().isoformat()
                    break
            
            # Salvar alterações
            with open(subscriptions_file, 'w') as f:
                json.dump(subscriptions, f, indent=2, default=str)
            
            # Rebaixar para plano gratuito
            self.upgrade_subscription(user_id, SubscriptionPlan.FREE)
            
            return True
            
        except Exception as e:
            print(f"Erro ao cancelar assinatura: {e}")
            return False
    
    def get_subscription_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obter detalhes da assinatura"""
        try:
            subscriptions_file = os.path.join("data", "subscriptions.json")
            
            if not os.path.exists(subscriptions_file):
                return None
            
            with open(subscriptions_file, 'r') as f:
                subscriptions = json.load(f)
            
            # Encontrar assinatura ativa do usuário
            for subscription in subscriptions:
                if (subscription.get("user_id") == user_id and 
                    subscription.get("status") == "active"):
                    return subscription
            
            return None
            
        except Exception as e:
            print(f"Erro ao obter detalhes da assinatura: {e}")
            return None
    
    def get_payment_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Obter histórico de pagamentos"""
        try:
            payments_file = os.path.join("data", "payments.json")
            
            if not os.path.exists(payments_file):
                return []
            
            with open(payments_file, 'r') as f:
                payments = json.load(f)
            
            # Filtrar pagamentos do usuário
            user_payments = [
                payment for payment in payments 
                if payment.get("user_id") == user_id
            ]
            
            # Ordenar por data (mais recentes primeiro)
            user_payments.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
            
            return user_payments
            
        except Exception as e:
            print(f"Erro ao obter histórico de pagamentos: {e}")
            return []
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Atualizar perfil do usuário com dados customizados"""
        try:
            profiles = self._load_member_profiles()
            
            for profile in profiles:
                if profile.get("user_id") == user_id:
                    # Fazer merge dos dados
                    profile.update(profile_data)
                    profile["updated_at"] = datetime.now().isoformat()
                    break
            else:
                # Se não encontrar, criar novo perfil
                new_profile = {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                new_profile.update(profile_data)
                profiles.append(new_profile)
            
            self._save_member_profiles(profiles)
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar perfil: {e}")
            return False
    
    def get_user_saved_prompts(self, user_id: str) -> List[Dict]:
        """Obter prompts salvos do usuário"""
        try:
            prompts_file = os.path.join("data", "saved_prompts.json")
            if not os.path.exists(prompts_file):
                return []
            
            with open(prompts_file, 'r', encoding='utf-8') as f:
                all_prompts = json.load(f)
            
            # Filtrar prompts do usuário
            user_prompts = [prompt for prompt in all_prompts if prompt.get('user_id') == user_id]
            return user_prompts
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar prompts salvos: {e}")
            return []
    
    def get_user_templates(self, user_id: str) -> List[Dict]:
        """Obter templates do usuário"""
        try:
            templates = self._load_templates()
            # Filtrar templates do usuário
            user_templates = [template for template in templates if template.get('user_id') == user_id]
            return user_templates
            
        except Exception as e:
            print(f"Erro ao carregar templates do usuário: {e}")
            return []
    
    def save_prompt(self, user_id: str, prompt_data: Dict) -> bool:
        """Salvar novo prompt do usuário"""
        try:
            prompts_file = os.path.join("data", "saved_prompts.json")
            
            # Carregar prompts existentes
            all_prompts = []
            if os.path.exists(prompts_file):
                try:
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        all_prompts = json.load(f)
                except json.JSONDecodeError:
                    all_prompts = []
            
            # Adicionar novo prompt
            new_prompt = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": prompt_data.get("title", "Prompt sem título"),
                "content": prompt_data.get("content", ""),
                "context": prompt_data.get("context", ""),
                "style": prompt_data.get("style", ""),
                "tone": prompt_data.get("tone", ""),
                "audience": prompt_data.get("audience", ""),
                "response": prompt_data.get("response", ""),
                "created_at": datetime.now().isoformat(),
                "tags": prompt_data.get("tags", []),
                "category": prompt_data.get("category", "general")
            }
            
            all_prompts.append(new_prompt)
            
            # Salvar
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(all_prompts, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar prompt: {e}")
            return False
    
    def check_monthly_quota(self, user_id: str) -> Dict[str, Any]:
        """Verificar quota mensal do usuário"""
        try:
            profile = self.get_member_profile(user_id)
            if not profile:
                return {"allowed": False, "reason": "Perfil não encontrado"}
            
            # Usar diretamente o enum como chave (não converter para string)
            plan_key = profile.subscription_plan
            
            # Obter quota do plano usando enum diretamente
            plan_limits = self.plan_quotas[plan_key]
            monthly_limit = plan_limits['monthly_prompts']
            
            if monthly_limit == -1:  # Enterprise ilimitado
                return {
                    "allowed": True, 
                    "used": profile.usage_current_month.get("prompts_generated", 0),
                    "limit": "unlimited",
                    "remaining": "unlimited"
                }
            
            used_this_month = profile.usage_current_month.get("prompts_generated", 0)
            remaining = monthly_limit - used_this_month
            
            return {
                "allowed": remaining > 0,
                "used": used_this_month,
                "limit": monthly_limit,
                "remaining": max(0, remaining),
                "reason": "Quota mensal excedida" if remaining <= 0 else None
            }
            
        except Exception as e:
            print(f"Erro ao verificar quota: {e}")
            return {"allowed": False, "reason": "Erro interno"}
    
    def increment_usage(self, user_id: str, usage_type: str = "prompts_generated") -> bool:
        """Incrementar uso mensal do usuário"""
        try:
            profiles = self._load_member_profiles()
            
            for profile_data in profiles:
                if profile_data['user_id'] == user_id:
                    # Incrementar contador
                    if 'usage_current_month' not in profile_data:
                        profile_data['usage_current_month'] = {}
                    
                    current_count = profile_data['usage_current_month'].get(usage_type, 0)
                    profile_data['usage_current_month'][usage_type] = current_count + 1
                    
                    # Atualizar estatísticas totais também
                    if 'usage_stats' not in profile_data:
                        profile_data['usage_stats'] = {}
                    
                    if usage_type == "prompts_generated":
                        total_prompts = profile_data['usage_stats'].get('total_prompts', 0)
                        profile_data['usage_stats']['total_prompts'] = total_prompts + 1
                    
                    # Salvar
                    self._save_member_profiles(profiles)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao incrementar uso: {e}")
            return False
    
    def create_member_profile_from_data(self, user_id: str, profile_data: dict) -> bool:
        """Criar perfil de membro a partir de dados personalizados"""
        try:
            profiles = self._load_member_profiles()
            
            # Verificar se perfil já existe
            for profile in profiles:
                if profile['user_id'] == user_id:
                    return False  # Perfil já existe
            
            # Adicionar novo perfil
            profiles.append(profile_data)
            
            # Salvar
            self._save_member_profiles(profiles)
            return True
            
        except Exception as e:
            print(f"Erro ao criar perfil personalizado: {e}")
            return False
    
    def save_public_template(self, user_id: str, template_data: dict) -> bool:
        """Salvar template público"""
        try:
            # Carregar templates existentes
            templates_file = self.templates_file
            
            if os.path.exists(templates_file):
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
            else:
                templates = []
            
            # Adicionar novo template
            templates.append(template_data)
            
            # Salvar
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar template público: {e}")
            return False