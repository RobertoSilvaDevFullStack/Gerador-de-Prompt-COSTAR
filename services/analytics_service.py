from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
from collections import defaultdict
import json

class AnalyticsService:
    def __init__(self):
        self.events_cache = []  # Em uma aplicação real, usar banco de dados
    
    async def track_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """Registrar evento de analytics"""
        try:
            event = {
                "name": event_name,
                "properties": properties or {},
                "timestamp": datetime.now().isoformat(),
                "session_id": properties.get("user_id") if properties else None
            }
            
            self.events_cache.append(event)
            
            # Manter apenas últimos 1000 eventos na memória
            if len(self.events_cache) > 1000:
                self.events_cache = self.events_cache[-1000:]
            
            print(f"Analytics: {event_name} - {properties}")
        except Exception as e:
            print(f"Erro ao registrar evento: {e}")
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Buscar estatísticas do dashboard do usuário"""
        try:
            # Filtrar eventos do usuário
            user_events = [
                e for e in self.events_cache 
                if e.get("properties", {}).get("user_id") == user_id
            ]
            
            # Calcular estatísticas básicas
            total_prompts = len([
                e for e in user_events 
                if e["name"] == "prompt_created"
            ])
            
            total_gemini_uses = len([
                e for e in user_events 
                if e["name"] == "gemini_used"
            ])
            
            templates_created = len([
                e for e in user_events 
                if e["name"] == "template_created"
            ])
            
            # Atividade dos últimos 30 dias
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_events = [
                e for e in user_events
                if datetime.fromisoformat(e["timestamp"]) >= thirty_days_ago
            ]
            
            return {
                "total_prompts": total_prompts,
                "total_gemini_uses": total_gemini_uses,
                "templates_created": templates_created,
                "activity_last_30_days": len(recent_events),
                "last_activity": user_events[-1]["timestamp"] if user_events else None
            }
        except Exception as e:
            print(f"Erro ao buscar dashboard: {e}")
            return {
                "total_prompts": 0,
                "total_gemini_uses": 0,
                "templates_created": 0,
                "activity_last_30_days": 0,
                "last_activity": None
            }
    
    async def get_usage_stats(self, user_id: str, periodo: str = "30d") -> Dict[str, Any]:
        """Buscar estatísticas de uso por período"""
        try:
            # Calcular período
            if periodo == "7d":
                cutoff_date = datetime.now() - timedelta(days=7)
            elif periodo == "30d":
                cutoff_date = datetime.now() - timedelta(days=30)
            elif periodo == "90d":
                cutoff_date = datetime.now() - timedelta(days=90)
            else:
                cutoff_date = datetime.now() - timedelta(days=30)
            
            # Filtrar eventos do período
            user_events = [
                e for e in self.events_cache
                if (e.get("properties", {}).get("user_id") == user_id and
                    datetime.fromisoformat(e["timestamp"]) >= cutoff_date)
            ]
            
            # Agrupar por tipo de evento
            event_counts = defaultdict(int)
            daily_activity = defaultdict(int)
            
            for event in user_events:
                event_counts[event["name"]] += 1
                day = datetime.fromisoformat(event["timestamp"]).strftime("%Y-%m-%d")
                daily_activity[day] += 1
            
            # Categorias mais usadas
            categories = defaultdict(int)
            for event in user_events:
                if event["name"] == "prompt_created":
                    categoria = event.get("properties", {}).get("categoria", "geral")
                    categories[categoria] += 1
            
            return {
                "periodo": periodo,
                "total_events": len(user_events),
                "event_counts": dict(event_counts),
                "daily_activity": dict(daily_activity),
                "top_categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        except Exception as e:
            print(f"Erro ao buscar estatísticas de uso: {e}")
            return {
                "periodo": periodo,
                "total_events": 0,
                "event_counts": {},
                "daily_activity": {},
                "top_categories": {}
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Buscar métricas gerais do sistema"""
        try:
            total_events = len(self.events_cache)
            
            # Usuários únicos
            unique_users = set()
            for event in self.events_cache:
                user_id = event.get("properties", {}).get("user_id")
                if user_id:
                    unique_users.add(user_id)
            
            # Eventos por tipo
            event_types = defaultdict(int)
            for event in self.events_cache:
                event_types[event["name"]] += 1
            
            return {
                "total_events": total_events,
                "unique_users": len(unique_users),
                "event_types": dict(event_types),
                "cache_size": len(self.events_cache)
            }
        except Exception as e:
            print(f"Erro ao buscar métricas do sistema: {e}")
            return {
                "total_events": 0,
                "unique_users": 0,
                "event_types": {},
                "cache_size": 0
            }