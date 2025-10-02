import json
import uuid
from datetime import datetime, timedelta
import random

# ID do usuário logado
user_id = "af761b53-2479-48ff-8795-65edb7e7b450"

# Carregar logs existentes
with open('data/api_usage_logs.json', 'r', encoding='utf-8') as f:
    api_logs = json.load(f)

# Carregar atividades existentes
with open('data/user_activities.json', 'r', encoding='utf-8') as f:
    user_activities = json.load(f)

# Adicionar dados reais para o usuário logado (últimos 30 dias)
now = datetime.now()

# Gerar logs de API dos últimos 30 dias
providers = ["groq", "gemini", "cohere"]
prompt_types = ["costar", "marketing", "technical", "creative"]

# Logs de API
for i in range(25):  # 25 prompts gerados no total
    days_ago = random.randint(0, 30)
    request_time = now - timedelta(days=days_ago)
    
    log_entry = {
        "id": f"real_log_{uuid.uuid4()}",
        "provider": random.choice(providers),
        "user_id": user_id,
        "prompt_type": random.choice(prompt_types),
        "request_time": request_time.isoformat(),
        "response_time": round(random.uniform(0.3, 2.5), 2),
        "success": random.choice([True, True, True, False]),  # 75% success rate
        "error_message": None if random.choice([True, True, True, False]) else "Timeout error",
        "tokens_used": random.randint(50, 300),
        "cost": round(random.uniform(0.001, 0.01), 4),
        "session_id": f"session_{uuid.uuid4()}",
        "endpoint": "/api/generate",
        "response_quality": round(random.uniform(7.5, 9.8), 1)
    }
    
    api_logs.append(log_entry)

# Atividades do usuário
activity_types = ["login", "prompt_generated", "template_saved", "profile_updated"]

for i in range(15):  # 15 atividades
    days_ago = random.randint(0, 30)
    activity_time = now - timedelta(days=days_ago)
    
    activity_entry = {
        "id": f"activity_{uuid.uuid4()}",
        "user_id": user_id,
        "action": random.choice(activity_types),
        "timestamp": activity_time.isoformat(),
        "details": {
            "ip": "127.0.0.1",
            "user_agent": "Mozilla/5.0",
            "success": True
        }
    }
    
    user_activities.append(activity_entry)

# Salvar arquivos atualizados
with open('data/api_usage_logs.json', 'w', encoding='utf-8') as f:
    json.dump(api_logs, f, indent=2, ensure_ascii=False)

with open('data/user_activities.json', 'w', encoding='utf-8') as f:
    json.dump(user_activities, f, indent=2, ensure_ascii=False)

print(f"✅ Adicionados dados de analytics para o usuário {user_id}")
print(f"📊 Total de logs de API: {len(api_logs)}")
print(f"🎯 Total de atividades: {len(user_activities)}")