import redis
import json
import os
from typing import Any, Optional, List
import asyncio

class CacheService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Testar conexão
            self.redis_client.ping()
        except:
            # Fallback para cache em memória se Redis não estiver disponível
            self.redis_client = None
            self.memory_cache = {}
            print("Redis não disponível, usando cache em memória")
    
    async def get(self, key: str) -> Optional[Any]:
        """Buscar valor do cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Cache em memória
                cache_entry = self.memory_cache.get(key)
                if cache_entry and cache_entry["expires"] > asyncio.get_event_loop().time():
                    return cache_entry["value"]
                elif cache_entry:
                    # Remover entrada expirada
                    del self.memory_cache[key]
            
            return None
        except Exception as e:
            print(f"Erro ao buscar cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Salvar valor no cache"""
        try:
            if self.redis_client:
                self.redis_client.setex(
                    key, 
                    expire, 
                    json.dumps(value, ensure_ascii=False, default=str)
                )
            else:
                # Cache em memória
                self.memory_cache[key] = {
                    "value": value,
                    "expires": asyncio.get_event_loop().time() + expire
                }
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    async def delete(self, key: str):
        """Remover valor do cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            print(f"Erro ao remover cache: {e}")
    
    async def delete_pattern(self, pattern: str):
        """Remover valores que correspondem ao padrão"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Para cache em memória, implementar matching simples
                keys_to_delete = []
                pattern_clean = pattern.replace("*", "")
                
                for key in self.memory_cache.keys():
                    if pattern_clean in key:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.memory_cache[key]
        except Exception as e:
            print(f"Erro ao remover cache por padrão: {e}")
    
    async def clear_expired(self):
        """Limpar entradas expiradas do cache em memória"""
        if not self.redis_client:
            current_time = asyncio.get_event_loop().time()
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry["expires"] <= current_time
            ]
            for key in expired_keys:
                del self.memory_cache[key]