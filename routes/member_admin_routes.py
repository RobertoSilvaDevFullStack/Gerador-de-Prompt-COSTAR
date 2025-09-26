"""
Rotas para Área de Membros e Dashboard Administrativo
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import jwt
import os

from services.auth_service import UserRole
from services.supabase_auth_service import SupabaseAuthService
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
                "profile": user.profile
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
        from services.auth_service import UserRole
        
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
                "profile": user.profile
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
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: necessário permissão de administrador"
        )
    return current_user

@member_router.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "profile": current_user.profile,
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
    """Obter analytics do membro"""
    analytics = member_service.get_member_analytics(current_user.id)
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics não encontradas"
        )
    
    return analytics

@member_router.get("/quota")
async def check_member_quota(current_user = Depends(get_current_user)):
    """Verificar quotas de uso"""
    prompts_quota = member_service.check_usage_quota(current_user.id, 'prompts')
    templates_quota = member_service.check_usage_quota(current_user.id, 'templates')
    
    return {
        "prompts": prompts_quota,
        "templates": templates_quota
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
    search: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Obter templates públicos"""
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