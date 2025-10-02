#!/usr/bin/env python3
"""
Script para criar dados de teste para o dashboard admin
- 5 perfis de usuários com diferentes planos
- 5 templates públicos
- 5 prompts salvos por usuário
"""

import sys
import os
import json
from datetime import datetime, timedelta
import uuid
import random

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.member_area_service import MemberAreaService, SubscriptionPlan
from services.supabase_auth_service import SupabaseAuthService, UserRole

def create_test_users():
    """Criar 5 usuários de teste"""
    print("👥 Criando 5 usuários de teste...")
    
    auth_service = SupabaseAuthService()
    
    users_data = [
        {
            "email": "joao.silva@email.com",
            "password": "senha123",
            "username": "João Silva",
            "plan": SubscriptionPlan.FREE,
            "role": UserRole.FREE,
            "created_days_ago": 30
        },
        {
            "email": "maria.santos@email.com", 
            "password": "senha123",
            "username": "Maria Santos",
            "plan": SubscriptionPlan.PREMIUM,
            "role": UserRole.PRO,
            "created_days_ago": 15
        },
        {
            "email": "pedro.oliveira@email.com",
            "password": "senha123", 
            "username": "Pedro Oliveira",
            "plan": SubscriptionPlan.FREE,
            "role": UserRole.FREE,
            "created_days_ago": 45
        },
        {
            "email": "ana.costa@email.com",
            "password": "senha123",
            "username": "Ana Costa", 
            "plan": SubscriptionPlan.ENTERPRISE,
            "role": UserRole.ENTERPRISE,
            "created_days_ago": 60
        },
        {
            "email": "carlos.ferreira@email.com",
            "password": "senha123",
            "username": "Carlos Ferreira",
            "plan": SubscriptionPlan.PREMIUM,
            "role": UserRole.PRO,
            "created_days_ago": 20
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            # Verificar se usuário já existe
            existing_user = auth_service.get_user_by_email(user_data["email"])
            if existing_user:
                print(f"   ⚠️  Usuário {user_data['email']} já existe, pulando...")
                created_users.append(existing_user.id)
                continue
            
            # Criar usuário no Supabase
            user = auth_service.register_user(
                email=user_data["email"],
                password=user_data["password"], 
                username=user_data["username"],
                role=user_data["role"]
            )
            
            if user:
                print(f"   ✅ Usuário criado: {user_data['username']} ({user_data['email']})")
                created_users.append(user.id)
            else:
                print(f"   ❌ Erro ao criar usuário: {user_data['email']}")
                
        except Exception as e:
            print(f"   ❌ Erro ao criar {user_data['email']}: {e}")
    
    return created_users, users_data

def create_member_profiles(user_ids, users_data):
    """Criar perfis de membros para os usuários"""
    print("\n👤 Criando perfis de membros...")
    
    member_service = MemberAreaService()
    
    for i, user_id in enumerate(user_ids):
        if i >= len(users_data):
            continue
            
        user_data = users_data[i]
        created_date = datetime.now() - timedelta(days=user_data["created_days_ago"])
        
        try:
            # Criar perfil personalizado
            profile_data = {
                "user_id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "subscription_plan": user_data["plan"].value,
                "created_at": created_date.isoformat(),
                "last_login": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "preferences": {
                    "default_style": random.choice(["professional", "creative", "technical", "casual"]),
                    "default_tone": random.choice(["formal", "friendly", "neutral", "enthusiastic"]),
                    "preferred_providers": random.choice([["gemini"], ["gemini", "groq"], ["gemini", "groq", "huggingface"]]),
                    "auto_save_prompts": random.choice([True, False]),
                    "email_notifications": random.choice([True, False]),
                    "theme": random.choice(["light", "dark"])
                },
                "usage_stats": {
                    "total_prompts": random.randint(0, 100),
                    "templates_created": random.randint(0, 10), 
                    "templates_shared": random.randint(0, 5)
                },
                "usage_current_month": {
                    "prompts_generated": random.randint(0, 30),
                    "api_calls": random.randint(0, 50),
                    "tokens_used": random.randint(0, 10000)
                }
            }
            
            # Salvar perfil
            success = member_service.create_member_profile_from_data(user_id, profile_data)
            if success:
                print(f"   ✅ Perfil criado: {user_data['username']} ({user_data['plan'].value})")
            else:
                print(f"   ❌ Erro ao criar perfil para: {user_data['username']}")
                
        except Exception as e:
            print(f"   ❌ Erro ao criar perfil para {user_data['username']}: {e}")

def create_test_templates(user_ids, users_data):
    """Criar 5 templates públicos"""
    print("\n📄 Criando 5 templates públicos...")
    
    member_service = MemberAreaService()
    
    templates_data = [
        {
            "title": "Email Marketing Profissional",
            "description": "Template para criar emails de marketing com alta taxa de conversão",
            "category": "Marketing",
            "context_template": "Criar um email marketing para {produto} direcionado para {publico_alvo}",
            "style": "Profissional",
            "tone": "Persuasivo",
            "format": "Email",
            "tags": ["marketing", "email", "vendas", "conversao"]
        },
        {
            "title": "Post para Redes Sociais",
            "description": "Template para posts engajadores nas redes sociais",
            "category": "Social Media", 
            "context_template": "Criar post para {rede_social} sobre {assunto} para gerar {objetivo}",
            "style": "Criativo",
            "tone": "Amigável",
            "format": "Post",
            "tags": ["social-media", "engajamento", "post", "criativo"]
        },
        {
            "title": "Artigo Técnico SEO",
            "description": "Template para artigos técnicos otimizados para SEO",
            "category": "SEO",
            "context_template": "Escrever artigo técnico sobre {tecnologia} focado em {palavra_chave}",
            "style": "Técnico",
            "tone": "Formal",
            "format": "Artigo",
            "tags": ["seo", "tecnico", "artigo", "blog"]
        },
        {
            "title": "Proposta Comercial",
            "description": "Template para propostas comerciais persuasivas",
            "category": "Vendas",
            "context_template": "Criar proposta comercial para {servico} para empresa {tipo_empresa}",
            "style": "Profissional", 
            "tone": "Persuasivo",
            "format": "Proposta",
            "tags": ["vendas", "proposta", "comercial", "business"]
        },
        {
            "title": "Conteúdo Educacional",
            "description": "Template para criar conteúdo educacional envolvente",
            "category": "Educação",
            "context_template": "Explicar {conceito} para {nivel_conhecimento} de forma {abordagem}",
            "style": "Educativo",
            "tone": "Didático", 
            "format": "Tutorial",
            "tags": ["educacao", "tutorial", "ensino", "didatico"]
        }
    ]
    
    for i, template_data in enumerate(templates_data):
        try:
            # Escolher um usuário aleatório como criador
            creator_index = i % len(user_ids)
            creator_id = user_ids[creator_index]
            creator_name = users_data[creator_index]["username"] if creator_index < len(users_data) else "Usuário"
            
            template = {
                "id": str(uuid.uuid4()),
                "title": template_data["title"],
                "description": template_data["description"],
                "category": template_data["category"],
                "context_template": template_data["context_template"], 
                "style": template_data["style"],
                "tone": template_data["tone"],
                "format": template_data["format"],
                "tags": template_data["tags"],
                "creator_id": creator_id,
                "creator_name": creator_name,
                "is_public": True,
                "usage_count": random.randint(1, 50),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            success = member_service.save_public_template(creator_id, template)
            if success:
                print(f"   ✅ Template criado: {template_data['title']} (por {creator_name})")
            else:
                print(f"   ❌ Erro ao criar template: {template_data['title']}")
                
        except Exception as e:
            print(f"   ❌ Erro ao criar template {template_data['title']}: {e}")

def create_saved_prompts(user_ids, users_data):
    """Criar prompts salvos para cada usuário"""
    print("\n💾 Criando prompts salvos para cada usuário...")
    
    member_service = MemberAreaService()
    
    prompt_examples = [
        {
            "title": "Estratégia de Marketing Digital",
            "context": "Campanha para lançamento de produto",
            "content": "Crie uma estratégia completa de marketing digital para o lançamento de um novo produto tech, incluindo cronograma, canais e métricas de sucesso.",
            "style": "Profissional",
            "tone": "Estratégico",
            "format": "Estratégia"
        },
        {
            "title": "Post Viral Instagram",
            "context": "Aumentar engajamento nas redes",
            "content": "Desenvolva um post criativo para Instagram que tenha potencial viral, usando trending topics e técnicas de storytelling.",
            "style": "Criativo", 
            "tone": "Energético",
            "format": "Post"
        },
        {
            "title": "Artigo SEO sobre IA",
            "context": "Blog corporativo sobre tecnologia",
            "content": "Escreva um artigo completo sobre Inteligência Artificial para empresas, otimizado para SEO com foco na palavra-chave 'IA para negócios'.",
            "style": "Técnico",
            "tone": "Informativo", 
            "format": "Artigo"
        },
        {
            "title": "Email de Follow-up",
            "context": "Nutrição de leads qualificados",
            "content": "Crie um email de follow-up personalizado para leads que demonstraram interesse em nosso produto, focando em benefits e social proof.",
            "style": "Comercial",
            "tone": "Persuasivo",
            "format": "Email"
        },
        {
            "title": "Tutorial Passo a Passo",
            "context": "Conteúdo educacional para usuários",
            "content": "Desenvolva um tutorial passo a passo para ensinar iniciantes a usar uma ferramenta de automação, com linguagem simples e exemplos práticos.",
            "style": "Educativo",
            "tone": "Didático",
            "format": "Tutorial"
        }
    ]
    
    for user_index, user_id in enumerate(user_ids):
        if user_index >= len(users_data):
            continue
            
        user_name = users_data[user_index]["username"]
        
        # Criar 2-5 prompts por usuário
        num_prompts = random.randint(2, 5)
        
        for i in range(num_prompts):
            try:
                prompt_data = random.choice(prompt_examples)
                
                prompt = {
                    "title": f"{prompt_data['title']} - {user_name}",
                    "context": prompt_data["context"],
                    "content": prompt_data["content"],
                    "style": prompt_data["style"],
                    "tone": prompt_data["tone"], 
                    "format": prompt_data["format"],
                    "tags": ["teste", "demo", prompt_data["style"].lower()],
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat(),
                    "rating": random.randint(3, 5),
                    "usage_count": random.randint(1, 10)
                }
                
                success = member_service.save_prompt(user_id, prompt)
                if success:
                    print(f"   ✅ Prompt salvo: {prompt['title']}")
                else:
                    print(f"   ❌ Erro ao salvar prompt para {user_name}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao criar prompt para {user_name}: {e}")

def update_analytics_data():
    """Atualizar dados de analytics para refletir os novos dados"""
    print("\n📊 Atualizando dados de analytics...")
    
    try:
        # Carregar dados existentes
        analytics_file = "data/member_analytics.json"
        
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r', encoding='utf-8') as f:
                analytics_data = json.load(f)
        else:
            analytics_data = {}
        
        # Atualizar métricas globais
        total_users = 6  # Admin + 5 usuários criados
        total_prompts = random.randint(50, 150)
        total_templates = 5
        
        global_analytics = {
            "total_users": total_users,
            "active_users_24h": random.randint(2, 5),
            "total_prompts_generated": total_prompts,
            "prompts_generated_24h": random.randint(5, 15),
            "total_templates": total_templates,
            "public_templates": total_templates,
            "avg_user_satisfaction": round(random.uniform(4.2, 4.8), 1),
            "total_api_calls": random.randint(200, 500),
            "api_calls_24h": random.randint(10, 30),
            "error_rate_24h": round(random.uniform(0.1, 2.0), 1),
            "avg_response_time_24h": round(random.uniform(150, 300), 0),
            "updated_at": datetime.now().isoformat()
        }
        
        analytics_data["global"] = global_analytics
        
        # Salvar analytics atualizados
        os.makedirs("data", exist_ok=True)
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
        
        print("   ✅ Analytics atualizados com sucesso")
        
    except Exception as e:
        print(f"   ❌ Erro ao atualizar analytics: {e}")

def main():
    """Função principal"""
    print("🚀 Criando dados de teste para o dashboard admin...")
    print("=" * 60)
    
    try:
        # 1. Criar usuários
        user_ids, users_data = create_test_users()
        
        if not user_ids:
            print("❌ Nenhum usuário foi criado. Abortando...")
            return
        
        # 2. Criar perfis de membros
        create_member_profiles(user_ids, users_data)
        
        # 3. Criar templates públicos
        create_test_templates(user_ids, users_data)
        
        # 4. Criar prompts salvos
        create_saved_prompts(user_ids, users_data)
        
        # 5. Atualizar analytics
        update_analytics_data()
        
        print("\n" + "=" * 60)
        print("🎉 Dados de teste criados com sucesso!")
        print("\n📋 Resumo:")
        print(f"   👥 Usuários criados: {len(user_ids)}")
        print(f"   📄 Templates públicos: 5")
        print(f"   💾 Prompts salvos: ~{len(user_ids) * 3}")
        print(f"   📊 Analytics atualizados")
        
        print("\n🔑 Credenciais de teste:")
        for user_data in users_data:
            print(f"   📧 {user_data['email']} / senha123 ({user_data['plan'].value})")
        
        print(f"\n🎯 Acesse o admin dashboard em:")
        print(f"   http://localhost:8000/frontend/admin-dashboard.html")
        print(f"   Login: admin@costar.com / admin123")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()