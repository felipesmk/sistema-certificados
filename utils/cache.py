# utils/cache.py
"""Sistema de cache para otimizar consultas frequentes."""

from functools import wraps
from datetime import datetime, timedelta
import threading

class SimpleCache:
    """Cache simples em memória com TTL."""
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get(self, key):
        """Obtém valor do cache se ainda válido."""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.now() < expiry:
                    return value
                else:
                    del self._cache[key]
            return None
    
    def set(self, key, value, ttl_seconds=300):
        """Define valor no cache com TTL."""
        with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expiry)
    
    def invalidate(self, key):
        """Remove item do cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Limpa todo o cache."""
        with self._lock:
            self._cache.clear()

# Instância global do cache
cache = SimpleCache()

def cached(ttl_seconds=300):
    """Decorator para cachear resultados de funções."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave única baseada na função e argumentos
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Tentar obter do cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache.set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator 