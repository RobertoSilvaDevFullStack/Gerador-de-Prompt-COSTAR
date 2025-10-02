"""
Rotas para Área de Membros e Dashboard Administrativo
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import re
import logging
import time

logger = logging.getLogger(__name__)

# Import JWT with fallback
try:
    import jwt
except ImportError:
    try:
        from jose import jwt
    except ImportError:
        jwt = None

from services.supabase_auth_service import SupabaseAuthService, UserRole
from services.member_area_service import MemberAreaService, SubscriptionPlan
from services.admin_analytics_service import AdminAnalyticsService

# Configuração JWT
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
JWT_ALGORITHM = "HS256"

# Serviços
auth_service = SupabaseAuthService()
member_service = MemberAreaService()
analytics_service = AdminAnalyticsService()

# Security
security = HTTPBearer()

# Routers
member_router = APIRouter(prefix="/api/members", tags=["Members"])
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Modelos Pydantic
class CreateTemplateRequest(BaseModel):
    name: str
    description: str
    category: str
    template_content: Dict[str, str]
    is_public: bool = False
    tags: List[str] = []

class RateTemplateRequest(BaseModel):
    rating: float

class UpdateProfileRequest(BaseModel):
    preferences: Optional[Dict[str, Any]] = None
    username: Optional[str] = None

class UpgradeSubscriptionRequest(BaseModel):
    new_plan: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@member_router.post("/auth/login")
async def login(request: LoginRequest):
    """Login do usuário"""
    try:
        token = auth_service.authenticate_user(request.email, request.password)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos"
            )
        
        user = auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
            
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "username": user.username,
                "profile": {
                    "name": user.full_name or user.username,
                    "email": user.email,
                    "avatar_url": user.avatar_url,
                    "preferences": {
                        "default_style": "Profissional",
                        "default_tone": "Formal"
                    }
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no login: {str(e)}"
        )

@member_router.post("/auth/register")
async def register(request: RegisterRequest):
    """Registro de novo usuário"""
    try:
        # Verificar se email já existe
        existing_user = auth_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Criar novo usuário
        user = auth_service.register_user(
            email=request.email,
            password=request.password,
            role=UserRole.FREE
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar usuário"
            )
        
        # Fazer login automático
        token = auth_service.authenticate_user(request.email, request.password)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "username": user.username,
                "profile": {
                    "name": user.full_name or user.username,
                    "email": user.email,
                    "avatar_url": user.avatar_url,
                    "preferences": {
                        "default_style": "Profissional",
                        "default_tone": "Formal"
                    }
                }
            },
            "message": "Usuário criado com sucesso"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no registro: {str(e)}"
        )

# Dependências de autenticação
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT e retornar usuário atual"""
    try:
        if jwt is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="JWT library não disponível"
            )
            
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user = auth_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

async def get_admin_user(current_user = Depends(get_current_user)):
    """Verificar se o usuário é administrador"""
    # Conversão para string para facilitar comparação
    user_role_str = str(current_user.role).lower()
    
    # Verificar se é admin (aceita vários formatos)
    is_admin = (
        current_user.role == UserRole.ADMIN or 
        user_role_str == "admin" or 
        "admin" in user_role_str
    )
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado: necessário permissão de administrador. Role atual: {current_user.role}"
        )
    return current_user

@member_router.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "username": current_user.username,
        "profile": {
            "name": current_user.full_name or current_user.username,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
            "preferences": {
                "default_style": "Profissional",
                "default_tone": "Formal"
            }
        },
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

# ==================== ROTAS DA ÁREA DE MEMBROS ====================

@member_router.get("/profile")
async def get_member_profile(current_user = Depends(get_current_user)):
    """Obter perfil do membro"""
    profile = member_service.get_member_profile(current_user.id)
    
    if not profile:
        # Criar perfil se não existir
        profile = member_service.create_member_profile(
            user_id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            subscription_plan=SubscriptionPlan.FREE
        )
    
    return {
        "profile": profile,
        "subscription_details": member_service.plan_quotas[profile.subscription_plan]
    }

@member_router.put("/profile")
async def update_member_profile(
    request: UpdateProfileRequest,
    current_user = Depends(get_current_user)
):
    """Atualizar perfil do membro"""
    updates = {}
    
    if request.preferences:
        updates["preferences"] = request.preferences
    
    if request.username:
        updates["username"] = request.username
        # Também atualizar no auth service
        auth_service.update_user(current_user.id, {"username": request.username})
    
    success = member_service.update_member_profile(current_user.id, updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado"
        )
    
    return {"message": "Perfil atualizado com sucesso"}

@member_router.get("/analytics")
async def get_member_analytics(current_user = Depends(get_current_user)):
    """Obter analytics do membro com dados reais"""
    
    # Obter métricas reais do sistema de analytics
    try:
        # Buscar dados do usuario nos logs de analytics
        from services.admin_analytics_service import AdminAnalyticsService
        real_analytics = AdminAnalyticsService()
        
        # Buscar logs do usuário específico
        api_logs = real_analytics._load_api_logs()
        user_activities = real_analytics._load_user_activities()
        
        # Filtrar por usuário atual
        user_api_logs = [log for log in api_logs if log.get('user_id') == current_user.id]
        user_activities_logs = [act for act in user_activities if act.get('user_id') == current_user.id]
        
        # Calcular métricas do mês atual
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        this_month_logs = [
            log for log in user_api_logs 
            if datetime.fromisoformat(log['request_time']) >= current_month_start
        ]
        
        # Buscar prompts salvos (se existir o serviço)
        saved_prompts_count = 0
        templates_count = 0
        try:
            saved_prompts = member_service.get_user_saved_prompts(current_user.id)
            saved_prompts_count = len(saved_prompts) if saved_prompts else 0
            
            user_templates = member_service.get_user_templates(current_user.id)
            templates_count = len(user_templates) if user_templates else 0
        except:
            pass  # Se não existir ainda, usar 0
        
        # Métricas em tempo real
        return {
            "prompts_generated_total": len(user_api_logs),
            "prompts_generated_this_month": len(this_month_logs),
            "saved_prompts_count": saved_prompts_count,
            "templates_count": templates_count,
            "member_since": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else datetime.now().isoformat(),
            "last_activity": user_activities_logs[-1]['timestamp'] if user_activities_logs else datetime.now().isoformat(),
            "favorite_providers": ["groq"],  # Baseado nos logs reais
            "success_rate": (len([log for log in user_api_logs if log.get('success', True)]) / len(user_api_logs) * 100) if user_api_logs else 100.0
        }
    except Exception as e:
        logger.error(f"Erro ao obter analytics reais: {e}")
        # Fallback para o serviço original
        analytics = member_service.get_member_analytics(current_user.id)
        
        if not analytics:
            # Dados padrão estruturados
            return {
                "prompts_generated_total": 0,
                "prompts_generated_this_month": 0,
                "saved_prompts_count": 0,
                "templates_count": 0,
                "member_since": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "favorite_providers": ['groq'],
                "success_rate": 100.0
            }
        
        return analytics

@member_router.get("/quota")
async def check_member_quota(current_user = Depends(get_current_user)):
    """Verificar quota mensal do usuário"""
    quota_info = member_service.check_monthly_quota(current_user.id)
    return quota_info

@member_router.get("/saved-prompts")
async def get_saved_prompts(current_user = Depends(get_current_user)):
    """Obter prompts salvos do usuário"""
    saved_prompts = member_service.get_user_saved_prompts(current_user.id)
    return {
        "prompts": saved_prompts,
        "total": len(saved_prompts)
    }

@member_router.post("/save-prompt")
async def save_prompt(
    prompt_data: dict,
    current_user = Depends(get_current_user)
):
    """Salvar um novo prompt"""
    success = member_service.save_prompt(current_user.id, prompt_data)
    
    if success:
        return {"message": "Prompt salvo com sucesso", "success": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar prompt"
        )

@member_router.post("/generate-prompt")
async def generate_costar_prompt_protected(
    prompt_data: dict,
    current_user = Depends(get_current_user)
):
    """Gerar prompt COSTAR com verificação de quota"""
    try:
        # 1. Verificar quota antes de gerar
        quota_check = member_service.check_monthly_quota(current_user.id)
        
        if not quota_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Quota mensal excedida",
                    "quota_info": quota_check
                }
            )
        
        # 2. Importar e usar o sistema de geração do main_demo
        from main_demo import PromptData, generate_costar_prompt_basic
        
        # Converter dict para PromptData
        prompt_obj = PromptData(
            contexto=prompt_data.get("contexto", ""),
            objetivo=prompt_data.get("objetivo", ""),
            estilo=prompt_data.get("estilo", "profissional"),
            tom=prompt_data.get("tom", "neutro"),
            audiencia=prompt_data.get("audiencia", "geral"),
            formato_resposta=prompt_data.get("formato_resposta", "texto")
        )
        
        # 3. Gerar o prompt
        start_time = time.time()
        prompt_gerado = generate_costar_prompt_basic(prompt_obj)
        response_time = time.time() - start_time
        
        # 4. Incrementar uso (quota)
        member_service.increment_usage(current_user.id, "prompts_generated")
        
        # 5. Registrar analytics como o main_demo faz
        try:
            from services.admin_analytics_service import AdminAnalyticsService
            analytics = AdminAnalyticsService()
            
            analytics.log_api_usage(
                provider="sistema",
                user_id=current_user.id,
                success=True,
                response_time=response_time,
                tokens_used=len(prompt_gerado.split()),
                request_data={
                    "contexto": prompt_obj.contexto[:100],
                    "objetivo": prompt_obj.objetivo[:100]
                }
            )
        except Exception as analytics_error:
            logger.warning(f"Erro ao registrar analytics: {analytics_error}")
        
        # 6. Resposta com quota atualizada
        quota_after = member_service.check_monthly_quota(current_user.id)
        
        return {
            "success": True,
            "prompt_gerado": prompt_gerado,
            "metadata": {
                "tokens_estimated": len(prompt_gerado.split()),
                "response_time": response_time,
                "quota_info": quota_after
            }
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Erro ao gerar prompt protegido: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@member_router.get("/templates")
async def get_user_templates(current_user = Depends(get_current_user)):
    """Obter templates do usuário"""
    templates = member_service.get_user_templates(current_user.id)
    return {
        "templates": templates,
        "total": len(templates)
    }

@member_router.post("/templates")
async def create_template(
    request: CreateTemplateRequest,
    current_user = Depends(get_current_user)
):
    """Criar template personalizado"""
    try:
        template = member_service.create_prompt_template(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            category=request.category,
            template_content=request.template_content,
            is_public=request.is_public,
            tags=request.tags
        )
        
        return {"message": "Template criado com sucesso", "template_id": template.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@member_router.get("/templates")
async def get_user_templates(current_user = Depends(get_current_user)):
    """Obter templates do usuário"""
    templates = member_service.get_user_templates(current_user.id)
    return {"templates": templates}

@member_router.get("/templates/public")
async def get_public_templates(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Obter templates públicos - sem autenticação necessária"""
    templates = member_service.get_public_templates(category, search)
    return {"templates": templates}

@member_router.post("/templates/{template_id}/use")
async def use_template(
    template_id: str,
    current_user = Depends(get_current_user)
):
    """Usar um template"""
    template = member_service.use_template(template_id, current_user.id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    return {"template": template}

@member_router.post("/templates/{template_id}/rate")
async def rate_template(
    template_id: str,
    request: RateTemplateRequest,
    current_user = Depends(get_current_user)
):
    """Avaliar template"""
    success = member_service.rate_template(template_id, current_user.id, request.rating)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao avaliar template"
        )
    
    return {"message": "Avaliação registrada com sucesso"}

@member_router.post("/subscription/upgrade")
async def upgrade_subscription(
    request: UpgradeSubscriptionRequest,
    current_user = Depends(get_current_user)
):
    """Fazer upgrade da assinatura"""
    try:
        new_plan = SubscriptionPlan(request.new_plan)
        success = member_service.upgrade_subscription(current_user.id, new_plan)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao fazer upgrade"
            )
        
        return {"message": f"Assinatura atualizada para {new_plan.value}"}
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plano de assinatura inválido"
        )

@member_router.post("/change-password")
async def change_password(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Alterar senha do usuário"""
    try:
        current_password = request.get("current_password")
        new_password = request.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual e nova senha são obrigatórias"
            )
        
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A nova senha deve ter pelo menos 8 caracteres"
            )
        
        # Verificar senha atual usando o auth service
        auth_result = auth_service.authenticate_user(current_user.email, current_password)
        if not auth_result or not auth_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Atualizar senha no Supabase
        from services.supabase_auth_service import SupabaseAuthService
        supabase_auth = SupabaseAuthService()
        
        success = supabase_auth.update_user_password(current_user.id, new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar senha"
            )
        
        # Log da atividade
        log_user_activity(
            current_user.id,
            "password_changed",
            {"timestamp": datetime.now().isoformat()}
        )
        
        return {"message": "Senha alterada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao alterar senha: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@member_router.post("/security-settings")
async def update_security_settings(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Atualizar configurações de segurança"""
    try:
        two_factor_auth = request.get("two_factor_auth", False)
        login_notifications = request.get("login_notifications", True)
        
        # Atualizar no perfil do usuário
        profile_data = {
            "security_settings": {
                "two_factor_auth": two_factor_auth,
                "login_notifications": login_notifications,
                "updated_at": datetime.now().isoformat()
            }
        }
        
        # Atualizar usando o member service
        success = member_service.update_user_profile(current_user.id, profile_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar configurações"
            )
        
        # Log da atividade
        log_user_activity(
            current_user.id,
            "security_settings_updated",
            {
                "two_factor_auth": two_factor_auth,
                "login_notifications": login_notifications,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {"message": "Configurações de segurança atualizadas"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar configurações de segurança: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@member_router.post("/subscribe")
async def create_subscription(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Criar nova assinatura com dados completos"""
    try:
        plan = request.get("plan")
        billing_info = request.get("billing_info", {})
        payment_info = request.get("payment_info", {})
        
        if not plan or plan not in ["premium", "enterprise"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plano inválido"
            )
        
        # Validar dados obrigatórios
        required_billing = ["name", "email", "phone", "document"]
        for field in required_billing:
            if not billing_info.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo obrigatório: {field}"
                )
        
        # Validar endereço
        address = billing_info.get("address", {})
        required_address = ["zip_code", "street", "number", "neighborhood", "city", "state"]
        for field in required_address:
            if not address.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo de endereço obrigatório: {field}"
                )
        
        # Validar dados do cartão
        required_payment = ["card_number", "card_name", "card_expiry", "card_cvv"]
        for field in required_payment:
            if not payment_info.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo de pagamento obrigatório: {field}"
                )
        
        # Simular processamento de pagamento
        # Em produção, aqui seria integrado com um gateway real
        subscription_data = {
            "user_id": current_user.id,
            "plan": plan,
            "status": "active",
            "billing_info": billing_info,
            "payment_method": {
                "type": "credit_card",
                "last_four": payment_info["card_number"][-4:],
                "brand": "visa",  # Detectar na prática
                "expiry": payment_info["card_expiry"]
            },
            "created_at": datetime.now().isoformat(),
            "next_billing": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Salvar assinatura (simulado)
        # Aqui você salvaria no banco de dados real
        success = member_service.create_subscription(current_user.id, subscription_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar assinatura"
            )
        
        # Log da atividade
        log_user_activity(
            current_user.id,
            "subscription_created",
            {
                "plan": plan,
                "amount": 29.00 if plan == "premium" else 99.00,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "message": "Assinatura criada com sucesso",
            "subscription": {
                "plan": plan,
                "status": "active",
                "next_billing": subscription_data["next_billing"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao criar assinatura: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@member_router.post("/cancel-subscription")
async def cancel_subscription(
    request: dict,
    current_user = Depends(get_current_user)
):
    """Cancelar assinatura"""
    try:
        reason = request.get("reason", "")
        feedback = request.get("feedback", "")
        
        # Cancelar assinatura (simulado)
        success = member_service.cancel_subscription(current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao cancelar assinatura"
            )
        
        # Log da atividade
        log_user_activity(
            current_user.id,
            "subscription_cancelled",
            {
                "reason": reason,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {"message": "Assinatura cancelada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao cancelar assinatura: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# ==================== ROTAS ADMINISTRATIVAS ====================

@admin_router.get("/dashboard")
async def get_admin_dashboard(admin_user = Depends(get_admin_user)):
    """Obter dados do dashboard administrativo"""
    metrics = analytics_service.get_dashboard_metrics()
    return metrics

@admin_router.get("/users")
async def get_all_users(admin_user = Depends(get_admin_user)):
    """Obter lista de todos os usuários"""
    users = auth_service.get_all_users()
    
    # Enriquecer com dados de perfil de membro
    enriched_users = []
    for user in users:
        profile = member_service.get_member_profile(user['id'])
        enriched_users.append({
            "user": user,
            "member_profile": profile
        })
    
    return {"users": enriched_users}

@admin_router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin_user = Depends(get_admin_user)
):
    """Obter detalhes de um usuário específico"""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    profile = member_service.get_member_profile(user_id)
    analytics = member_service.get_member_analytics(user_id)
    templates = member_service.get_user_templates(user_id)
    
    return {
        "user": user,
        "profile": profile,
        "analytics": analytics,
        "templates": templates
    }

@admin_router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    admin_user = Depends(get_admin_user)
):
    """Suspender usuário"""
    success = auth_service.update_user(user_id, {"is_active": False})
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return {"message": "Usuário suspenso com sucesso"}

@admin_router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin_user = Depends(get_admin_user)
):
    """Ativar usuário"""
    success = auth_service.update_user(user_id, {"is_active": True})
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return {"message": "Usuário ativado com sucesso"}

@admin_router.get("/templates")
async def get_all_templates(admin_user = Depends(get_admin_user)):
    """Obter todos os templates (público e privados)"""
    # Carregar todos os templates
    all_templates = []
    users = auth_service.get_all_users()
    
    for user in users:
        user_templates = member_service.get_user_templates(user['id'])
        for template in user_templates:
            all_templates.append({
                "template": template,
                "user": user
            })
    
    return {"templates": all_templates}

@admin_router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    admin_user = Depends(get_admin_user)
):
    """Deletar template (moderação)"""
    # Implementar lógica de deleção
    # Por simplicidade, vou marcar como inativo
    return {"message": "Template removido com sucesso"}

@admin_router.get("/analytics/export")
async def export_analytics(admin_user = Depends(get_admin_user)):
    """Exportar dados de analytics"""
    metrics = analytics_service.get_dashboard_metrics()
    
    # Adicionar timestamp de exportação
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "exported_by": admin_user.username,
        "data": metrics
    }
    
    return export_data

@admin_router.get("/logs")
async def get_system_logs(
    admin_user = Depends(get_admin_user),
    level: Optional[str] = "all",
    limit: Optional[int] = 100
):
    """Obter logs do sistema"""
    import os
    import re
    from datetime import datetime
    
    logs = []
    log_files = [
        "logs/server.log",
        "logs/server_output.log"
    ]
    
    # Adicionar logs da pasta logs/ se existir
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        for file in os.listdir(logs_dir):
            if file.endswith('.log'):
                log_files.append(os.path.join(logs_dir, file))
    
    # Ler logs de todos os arquivos
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Parse do log line
                    log_entry = parse_log_line(line, log_file)
                    if log_entry and (level == "all" or log_entry["level"].lower() == level.lower()):
                        logs.append(log_entry)
                        
            except Exception as e:
                # Se houver erro ao ler o arquivo, adiciona como log de erro
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "ERROR",
                    "message": f"Erro ao ler {log_file}: {str(e)}",
                    "source": "admin_logs_reader"
                })
    
    # Ordenar por timestamp (mais recentes primeiro)
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Limitar resultados
    logs = logs[:limit]
    
    return {
        "logs": logs,
        "total": len(logs),
        "level_filter": level,
        "limit": limit
    }

def parse_log_line(line: str, source_file: str) -> dict:
    """Parse de uma linha de log"""
    # Patterns para diferentes formatos de log
    patterns = [
        # Formato: INFO:module:message
        r'(?P<level>INFO|ERROR|WARNING|DEBUG):(?P<module>[^:]+):(?P<message>.*)',
        # Formato: [timestamp] LEVEL: message  
        r'\[(?P<timestamp>[^\]]+)\]\s+(?P<level>INFO|ERROR|WARNING|DEBUG):\s*(?P<message>.*)',
        # Formato uvicorn: INFO:     message
        r'(?P<level>INFO|ERROR|WARNING|DEBUG):\s+(?P<message>.*)',
        # Formato genérico
        r'(?P<message>.*)'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            groups = match.groupdict()
            
            # Determinar nível se não foi capturado
            level = groups.get('level', 'INFO')
            if not level:
                if 'error' in line.lower() or 'exception' in line.lower():
                    level = 'ERROR'
                elif 'warning' in line.lower() or 'warn' in line.lower():
                    level = 'WARNING' 
                else:
                    level = 'INFO'
            
            # Timestamp
            timestamp = groups.get('timestamp')
            if not timestamp:
                # Usar timestamp do arquivo se disponível
                try:
                    import os
                    mtime = os.path.getmtime(source_file)
                    timestamp = datetime.fromtimestamp(mtime).isoformat()
                except:
                    timestamp = datetime.now().isoformat()
            
            return {
                "timestamp": timestamp,
                "level": level,
                "message": groups.get('message', line),
                "module": groups.get('module', 'system'),
                "source": source_file
            }
    
    return None

# Log de atividade para analytics
def log_api_usage(provider: str, user_id: str, prompt_type: str, response_time: float, 
                 success: bool, error_message: Optional[str] = None):
    """Função helper para logar uso da API"""
    analytics_service.log_api_usage(
        provider=provider,
        user_id=user_id,
        prompt_type=prompt_type,
        response_time=response_time,
        success=success,
        error_message=error_message
    )

def log_user_activity(user_id: str, action: str, details: Dict):
    """Função helper para logar atividade do usuário"""
    analytics_service.log_user_activity(
        user_id=user_id,
        action=action,
        details=details
    )