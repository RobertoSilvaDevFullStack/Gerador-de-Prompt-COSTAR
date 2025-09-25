"""
Sistema de Analytics e Dashboard Administrativo
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid
from collections import defaultdict, Counter

@dataclass
class APIUsageLog:
    id: str
    provider: str
    user_id: Optional[str]
    prompt_type: str  # 'costar', 'analysis', 'general'
    request_time: datetime
    response_time: float
    success: bool
    error_message: Optional[str] = None
    tokens_used: int = 0
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class UserActivity:
    id: str
    user_id: str
    action: str  # 'login', 'logout', 'generate_prompt', 'save_prompt', 'delete_prompt'
    timestamp: datetime
    details: Dict
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class SystemMetrics:
    timestamp: datetime
    total_users: int
    active_users_24h: int
    total_prompts_generated: int
    prompts_generated_24h: int
    api_calls_24h: int
    error_rate_24h: float
    most_used_provider: str
    avg_response_time: float

class AdminAnalyticsService:
    def __init__(self):
        self.api_logs_file = 'data/api_usage_logs.json'
        self.user_activity_file = 'data/user_activities.json'
        self.metrics_file = 'data/system_metrics.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Criar arquivos de dados se não existirem"""
        os.makedirs('data', exist_ok=True)
        
        for file_path in [self.api_logs_file, self.user_activity_file, self.metrics_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def log_api_usage(self, provider: str, user_id: Optional[str], prompt_type: str, 
                     response_time: float, success: bool, error_message: Optional[str] = None,
                     tokens_used: int = 0, ip_address: str = "", user_agent: str = ""):
        """Registrar uso da API"""
        log_entry = APIUsageLog(
            id=str(uuid.uuid4()),
            provider=provider,
            user_id=user_id,
            prompt_type=prompt_type,
            request_time=datetime.now(),
            response_time=response_time,
            success=success,
            error_message=error_message,
            tokens_used=tokens_used,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logs = self._load_api_logs()
        logs.append(asdict(log_entry))
        self._save_api_logs(logs)
    
    def log_user_activity(self, user_id: str, action: str, details: Dict,
                         ip_address: str = "", user_agent: str = ""):
        """Registrar atividade do usuário"""
        activity = UserActivity(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            timestamp=datetime.now(),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        activities = self._load_user_activities()
        activities.append(asdict(activity))
        self._save_user_activities(activities)
    
    def get_dashboard_metrics(self) -> Dict:
        """Obter métricas para o dashboard administrativo"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Carregar dados
        api_logs = self._load_api_logs()
        user_activities = self._load_user_activities()
        
        # Filtros por período
        logs_24h = [log for log in api_logs if datetime.fromisoformat(log['request_time']) >= last_24h]
        logs_7d = [log for log in api_logs if datetime.fromisoformat(log['request_time']) >= last_7d]
        
        activities_24h = [act for act in user_activities if datetime.fromisoformat(act['timestamp']) >= last_24h]
        activities_7d = [act for act in user_activities if datetime.fromisoformat(act['timestamp']) >= last_7d]
        
        # Métricas de API
        api_metrics = self._calculate_api_metrics(api_logs, logs_24h, logs_7d)
        
        # Métricas de usuários
        user_metrics = self._calculate_user_metrics(user_activities, activities_24h, activities_7d)
        
        # Métricas de prompts
        prompt_metrics = self._calculate_prompt_metrics(api_logs, logs_24h, logs_7d)
        
        # Performance
        performance_metrics = self._calculate_performance_metrics(logs_24h)
        
        return {
            'overview': {
                'total_api_calls': len(api_logs),
                'api_calls_24h': len(logs_24h),
                'total_users': len(set(act['user_id'] for act in user_activities if act['user_id'])),
                'active_users_24h': len(set(act['user_id'] for act in activities_24h if act['user_id'])),
                'error_rate_24h': (len([log for log in logs_24h if not log['success']]) / len(logs_24h) * 100) if logs_24h else 0,
                'avg_response_time_24h': sum(log['response_time'] for log in logs_24h) / len(logs_24h) if logs_24h else 0
            },
            'api_usage': api_metrics,
            'user_activity': user_metrics,
            'prompt_generation': prompt_metrics,
            'performance': performance_metrics,
            'charts_data': self._generate_charts_data(api_logs, user_activities)
        }
    
    def _calculate_api_metrics(self, all_logs: List, logs_24h: List, logs_7d: List) -> Dict:
        """Calcular métricas das APIs"""
        # Contadores por provedor
        provider_usage = Counter(log['provider'] for log in all_logs)
        provider_usage_24h = Counter(log['provider'] for log in logs_24h)
        
        # Taxa de sucesso por provedor
        provider_success = {}
        for provider in provider_usage.keys():
            provider_logs = [log for log in all_logs if log['provider'] == provider]
            success_count = sum(1 for log in provider_logs if log['success'])
            provider_success[provider] = (success_count / len(provider_logs) * 100) if provider_logs else 0
        
        # Tempo de resposta por provedor
        provider_response_times = {}
        for provider in provider_usage.keys():
            provider_logs = [log for log in logs_24h if log['provider'] == provider]
            avg_time = sum(log['response_time'] for log in provider_logs) / len(provider_logs) if provider_logs else 0
            provider_response_times[provider] = avg_time
        
        return {
            'provider_usage': dict(provider_usage),
            'provider_usage_24h': dict(provider_usage_24h),
            'provider_success_rates': provider_success,
            'provider_response_times': provider_response_times,
            'most_used_provider': provider_usage.most_common(1)[0][0] if provider_usage else 'none',
            'total_requests_7d': len(logs_7d)
        }
    
    def _calculate_user_metrics(self, all_activities: List, activities_24h: List, activities_7d: List) -> Dict:
        """Calcular métricas de usuários"""
        # Usuários únicos
        unique_users = set(act['user_id'] for act in all_activities if act['user_id'])
        unique_users_24h = set(act['user_id'] for act in activities_24h if act['user_id'])
        unique_users_7d = set(act['user_id'] for act in activities_7d if act['user_id'])
        
        # Ações mais comuns
        action_counts = Counter(act['action'] for act in all_activities)
        action_counts_24h = Counter(act['action'] for act in activities_24h)
        
        # Padrões de uso por hora
        hourly_activity = defaultdict(int)
        for activity in activities_24h:
            hour = datetime.fromisoformat(activity['timestamp']).hour
            hourly_activity[hour] += 1
        
        return {
            'total_unique_users': len(unique_users),
            'active_users_24h': len(unique_users_24h),
            'active_users_7d': len(unique_users_7d),
            'action_distribution': dict(action_counts),
            'action_distribution_24h': dict(action_counts_24h),
            'hourly_activity_pattern': dict(hourly_activity),
            'user_retention_7d': len(unique_users_7d) / len(unique_users) * 100 if unique_users else 0
        }
    
    def _calculate_prompt_metrics(self, all_logs: List, logs_24h: List, logs_7d: List) -> Dict:
        """Calcular métricas de geração de prompts"""
        # Tipos de prompts
        prompt_types = Counter(log['prompt_type'] for log in all_logs)
        prompt_types_24h = Counter(log['prompt_type'] for log in logs_24h)
        
        # Tokens utilizados
        total_tokens = sum(log.get('tokens_used', 0) for log in all_logs)
        tokens_24h = sum(log.get('tokens_used', 0) for log in logs_24h)
        
        # Prompts por dia (últimos 7 dias)
        daily_prompts = defaultdict(int)
        for log in logs_7d:
            date = datetime.fromisoformat(log['request_time']).date()
            daily_prompts[date.isoformat()] += 1
        
        return {
            'total_prompts_generated': len(all_logs),
            'prompts_generated_24h': len(logs_24h),
            'prompts_generated_7d': len(logs_7d),
            'prompt_type_distribution': dict(prompt_types),
            'prompt_type_distribution_24h': dict(prompt_types_24h),
            'total_tokens_used': total_tokens,
            'tokens_used_24h': tokens_24h,
            'daily_generation_pattern': dict(daily_prompts),
            'avg_prompts_per_user': len(all_logs) / len(set(log['user_id'] for log in all_logs if log['user_id'])) if any(log['user_id'] for log in all_logs) else 0
        }
    
    def _calculate_performance_metrics(self, logs_24h: List) -> Dict:
        """Calcular métricas de performance"""
        if not logs_24h:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'p95_response_time': 0,
                'uptime_percentage': 100,
                'error_breakdown': {}
            }
        
        response_times = [log['response_time'] for log in logs_24h]
        response_times.sort()
        
        # Percentil 95
        p95_index = int(len(response_times) * 0.95)
        p95_time = response_times[p95_index] if p95_index < len(response_times) else response_times[-1]
        
        # Breakdown de erros
        error_logs = [log for log in logs_24h if not log['success']]
        error_breakdown = Counter(log.get('error_message', 'Unknown') for log in error_logs)
        
        # Uptime (baseado em taxa de sucesso)
        success_rate = (len(logs_24h) - len(error_logs)) / len(logs_24h) * 100
        
        return {
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': p95_time,
            'uptime_percentage': success_rate,
            'error_breakdown': dict(error_breakdown),
            'total_errors_24h': len(error_logs)
        }
    
    def _generate_charts_data(self, api_logs: List, user_activities: List) -> Dict:
        """Gerar dados para gráficos do dashboard"""
        # Últimos 7 dias
        last_7d = datetime.now() - timedelta(days=7)
        
        # Dados para gráfico de linha (últimos 7 dias)
        daily_data = {}
        
        # Inicializar com estrutura correta
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).date()
            date_str = date.isoformat()
            daily_data[date_str] = {'api_calls': 0, 'unique_users': set()}
        
        for log in api_logs:
            log_date = datetime.fromisoformat(log['request_time'])
            if log_date >= last_7d:
                date_str = log_date.date().isoformat()
                if date_str in daily_data:
                    daily_data[date_str]['api_calls'] += 1
                    if log['user_id']:
                        daily_data[date_str]['unique_users'].add(log['user_id'])
        
        # Converter para formato de gráfico
        chart_dates = []
        chart_api_calls = []
        chart_users = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).date()
            date_str = date.isoformat()
            chart_dates.append(date_str)
            chart_api_calls.append(daily_data[date_str]['api_calls'])
            chart_users.append(len(daily_data[date_str]['unique_users']))
        
        # Dados para gráfico de pizza (distribuição de provedores)
        provider_data = Counter(log['provider'] for log in api_logs)
        
        return {
            'timeline': {
                'dates': chart_dates,
                'api_calls': chart_api_calls,
                'active_users': chart_users
            },
            'provider_distribution': {
                'labels': list(provider_data.keys()),
                'data': list(provider_data.values())
            }
        }
    
    def _load_api_logs(self) -> List:
        """Carregar logs de API"""
        try:
            with open(self.api_logs_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_api_logs(self, logs: List):
        """Salvar logs de API"""
        # Manter apenas os últimos 10000 logs para performance
        if len(logs) > 10000:
            logs = logs[-10000:]
        
        with open(self.api_logs_file, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
    
    def _load_user_activities(self) -> List:
        """Carregar atividades de usuários"""
        try:
            with open(self.user_activity_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_user_activities(self, activities: List):
        """Salvar atividades de usuários"""
        # Manter apenas os últimos 5000 registros
        if len(activities) > 5000:
            activities = activities[-5000:]
        
        with open(self.user_activity_file, 'w') as f:
            json.dump(activities, f, indent=2, default=str)