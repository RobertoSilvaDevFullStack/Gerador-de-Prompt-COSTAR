"""
Endpoints para status e diagnóstico do sistema
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import asyncio

from services.integrated_data_service import get_data_service
from config.supabase_config import check_configuration

router = APIRouter(prefix="/api/status", tags=["System Status"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Verificação de saúde do sistema"""
    data_service = get_data_service()
    
    # Testa conexão com backend
    backend_status = await data_service.test_connection()
    
    # Verifica configuração Supabase
    supabase_config = check_configuration()
    
    return {
        "status": "healthy",
        "backend": backend_status,
        "supabase_config": {
            "configured": supabase_config['ready_for_public'],
            "admin_access": supabase_config['ready_for_admin'],
            "validation": supabase_config['validation']
        },
        "mode": backend_status['mode'],
        "timestamp": "2024-01-01T00:00:00Z"  # Será atualizado automaticamente
    }

@router.get("/database")
async def database_status() -> Dict[str, Any]:
    """Status detalhado do banco de dados"""
    data_service = get_data_service()
    
    if data_service.mode == "demo":
        return {
            "mode": "demo",
            "status": "active",
            "tables": {
                "prompts": len(data_service.demo_data['prompts']),
                "templates": len(data_service.demo_data['templates']),
                "ai_logs": len(data_service.demo_data['ai_logs'])
            },
            "message": "Executando em modo demonstração com dados em memória"
        }
    
    elif data_service.mode == "supabase":
        try:
            # Testa conexão e lista tabelas
            connection_test = await data_service.supabase_service.test_connection(use_admin=True)
            
            if connection_test:
                # Query para verificar tabelas
                tables_query = """
                SELECT table_name, 
                       (SELECT count(*) FROM information_schema.columns 
                        WHERE table_name=t.table_name AND table_schema='public') as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
                
                result = await data_service.supabase_service.execute_query(tables_query, use_admin=True)
                
                if result['success']:
                    tables_info = {table['table_name']: table['column_count'] for table in result['data']}
                    
                    return {
                        "mode": "supabase",
                        "status": "connected",
                        "connection": "ok",
                        "tables": tables_info,
                        "message": f"Conectado ao Supabase com {len(tables_info)} tabelas"
                    }
                else:
                    return {
                        "mode": "supabase",
                        "status": "connection_ok_query_failed",
                        "connection": "ok",
                        "error": result.get('error'),
                        "message": "Conexão ok mas falha ao consultar tabelas"
                    }
            else:
                return {
                    "mode": "supabase",
                    "status": "connection_failed",
                    "connection": "failed",
                    "message": "Falha na conexão com Supabase"
                }
                
        except Exception as e:
            return {
                "mode": "supabase",
                "status": "error",
                "connection": "exception",
                "error": str(e),
                "message": "Erro ao verificar status do Supabase"
            }
    
    else:
        return {
            "mode": "unknown",
            "status": "error",
            "message": "Modo de operação desconhecido"
        }

@router.get("/features")
async def features_status() -> Dict[str, Any]:
    """Status das funcionalidades do sistema"""
    data_service = get_data_service()
    backend_status = await data_service.test_connection()
    
    # Verifica IAs disponíveis
    import os
    ai_providers = {
        'groq': bool(os.getenv('GROQ_API_KEY', '').strip()),
        'gemini': bool(os.getenv('GEMINI_API_KEY', '').strip()),
        'huggingface': bool(os.getenv('HUGGINGFACE_API_KEY', '').strip()),
        'cohere': bool(os.getenv('COHERE_API_KEY', '').strip()),
        'together': bool(os.getenv('TOGETHER_API_KEY', '').strip())
    }
    
    return {
        "data_persistence": {
            "available": True,
            "mode": backend_status['mode'],
            "status": backend_status['status']
        },
        "ai_providers": {
            "available": ai_providers,
            "total_configured": sum(ai_providers.values()),
            "multi_ai_enabled": sum(ai_providers.values()) > 1
        },
        "features": {
            "prompt_generation": True,
            "prompt_analysis": sum(ai_providers.values()) > 0,
            "user_management": backend_status['mode'] == 'supabase',
            "data_persistence": True,
            "admin_dashboard": True,
            "member_area": True,
            "template_system": True
        }
    }

@router.post("/test-connection")
async def test_connection() -> Dict[str, Any]:
    """Testa conexão forçada com todos os sistemas"""
    results = {}
    
    # Testa serviço de dados
    data_service = get_data_service()
    results['data_service'] = await data_service.test_connection()
    
    # Testa configuração Supabase
    supabase_config = check_configuration()
    results['supabase_config'] = supabase_config
    
    # Testa IAs (se disponível - importação condicional)
    try:
        from services.multi_ai_service import MultiAIService
        ai_service = MultiAIService()
        
        # Teste rápido com prompt simples
        test_result = await ai_service.generate_text(
            "Teste de conexão - responda apenas 'OK'",
            max_tokens=10,
            temperature=0.1
        )
        
        results['ai_service'] = {
            'available': True,
            'working': test_result['success'],
            'provider_used': test_result.get('provider_used', 'unknown'),
            'response_preview': test_result.get('result', '')[:50] if test_result.get('result') else None
        }
        
    except Exception as e:
        results['ai_service'] = {
            'available': False,
            'error': str(e)
        }
    
    # Status geral
    all_systems_ok = (
        results['data_service']['connected'] and
        results.get('ai_service', {}).get('working', False)
    )
    
    return {
        "overall_status": "healthy" if all_systems_ok else "degraded",
        "systems": results,
        "recommendations": _get_system_recommendations(results)
    }

def _get_system_recommendations(results: Dict[str, Any]) -> List[str]:
    """Gera recomendações baseadas no status dos sistemas"""
    recommendations = []
    
    # Recomendações para dados
    if results['data_service']['mode'] == 'demo':
        recommendations.append("Configure Supabase para persistência de dados em produção")
    
    # Recomendações para IA
    if not results.get('ai_service', {}).get('working', False):
        recommendations.append("Configure pelo menos uma chave de API de IA para análise de prompts")
    
    # Recomendações para Supabase
    supabase_status = results.get('supabase_config', {})
    if not supabase_status.get('ready_for_public', False):
        recommendations.append("Configure variáveis SUPABASE_URL e SUPABASE_ANON_KEY")
    
    if not supabase_status.get('ready_for_admin', False):
        recommendations.append("Configure SUPABASE_SERVICE_ROLE_KEY para funcionalidades administrativas")
    
    return recommendations