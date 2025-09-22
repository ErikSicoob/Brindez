"""
Sistema de otimização de performance
"""

import time
import threading
import functools
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta

class PerformanceMonitor:
    """Monitor de performance da aplicação"""
    
    def __init__(self):
        """Inicializa o monitor"""
        self.metrics = {}
        self.cache = {}
        self.cache_ttl = {}
        self.lock = threading.Lock()
    
    def measure_time(self, operation_name: str):
        """Decorator para medir tempo de execução"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.record_metric(operation_name, execution_time, True)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.record_metric(operation_name, execution_time, False)
                    raise e
            return wrapper
        return decorator
    
    def record_metric(self, operation: str, execution_time: float, success: bool):
        """Registra métrica de performance"""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'failed_calls': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'last_call': None
                }
            
            metric = self.metrics[operation]
            metric['total_calls'] += 1
            metric['total_time'] += execution_time
            metric['min_time'] = min(metric['min_time'], execution_time)
            metric['max_time'] = max(metric['max_time'], execution_time)
            metric['last_call'] = datetime.now().isoformat()
            
            if success:
                metric['successful_calls'] += 1
            else:
                metric['failed_calls'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance"""
        with self.lock:
            result = {}
            for operation, metric in self.metrics.items():
                avg_time = metric['total_time'] / metric['total_calls'] if metric['total_calls'] > 0 else 0
                success_rate = (metric['successful_calls'] / metric['total_calls'] * 100) if metric['total_calls'] > 0 else 0
                
                result[operation] = {
                    'total_calls': metric['total_calls'],
                    'success_rate': round(success_rate, 2),
                    'avg_time': round(avg_time, 4),
                    'min_time': round(metric['min_time'], 4) if metric['min_time'] != float('inf') else 0,
                    'max_time': round(metric['max_time'], 4),
                    'last_call': metric['last_call']
                }
            
            return result
    
    def reset_metrics(self):
        """Reseta todas as métricas"""
        with self.lock:
            self.metrics.clear()

class CacheManager:
    """Gerenciador de cache para otimização"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutos padrão
        """Inicializa o gerenciador de cache"""
        self.cache = {}
        self.cache_ttl = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
    
    def cache_result(self, ttl: Optional[int] = None):
        """Decorator para cache de resultados"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Criar chave do cache
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                
                # Verificar se existe no cache e não expirou
                if self.get_from_cache(cache_key) is not None:
                    return self.get_from_cache(cache_key)
                
                # Executar função e cachear resultado
                result = func(*args, **kwargs)
                self.set_cache(cache_key, result, ttl or self.default_ttl)
                
                return result
            return wrapper
        return decorator
    
    def set_cache(self, key: str, value: Any, ttl: int):
        """Define valor no cache"""
        with self.lock:
            self.cache[key] = value
            self.cache_ttl[key] = datetime.now() + timedelta(seconds=ttl)
    
    def get_from_cache(self, key: str) -> Any:
        """Obtém valor do cache"""
        with self.lock:
            if key not in self.cache:
                return None
            
            # Verificar se expirou
            if datetime.now() > self.cache_ttl.get(key, datetime.min):
                del self.cache[key]
                del self.cache_ttl[key]
                return None
            
            return self.cache[key]
    
    def invalidate_cache(self, pattern: str = None):
        """Invalida cache por padrão"""
        with self.lock:
            if pattern is None:
                self.cache.clear()
                self.cache_ttl.clear()
            else:
                keys_to_remove = [key for key in self.cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del self.cache[key]
                    del self.cache_ttl[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        with self.lock:
            total_items = len(self.cache)
            expired_items = sum(1 for ttl in self.cache_ttl.values() if datetime.now() > ttl)
            
            return {
                'total_items': total_items,
                'active_items': total_items - expired_items,
                'expired_items': expired_items,
                'cache_keys': list(self.cache.keys())
            }

class DatabaseOptimizer:
    """Otimizador de consultas ao banco"""
    
    def __init__(self):
        """Inicializa o otimizador"""
        self.query_cache = CacheManager(60)  # Cache de 1 minuto para queries
        self.connection_pool = []
        self.max_connections = 5
    
    def optimize_query(self, query: str, params: tuple = None) -> str:
        """Otimiza uma query SQL"""
        # Adicionar LIMIT se não existir em SELECTs sem WHERE específico
        if query.strip().upper().startswith('SELECT') and 'LIMIT' not in query.upper():
            if 'WHERE' not in query.upper() or 'COUNT(*)' not in query.upper():
                query += ' LIMIT 1000'
        
        return query
    
    def should_use_index(self, table: str, column: str) -> bool:
        """Verifica se deve usar índice"""
        # Índices recomendados
        recommended_indexes = {
            'brindes': ['codigo', 'categoria_id', 'filial_id'],
            'movimentacoes': ['brinde_id', 'data_hora', 'tipo'],
            'usuarios': ['username'],
            'logs_auditoria': ['tabela', 'data_hora']
        }
        
        return column in recommended_indexes.get(table, [])

class UIOptimizer:
    """Otimizador de interface"""
    
    def __init__(self):
        """Inicializa o otimizador de UI"""
        self.widget_cache = {}
        self.lazy_load_threshold = 100
    
    def should_lazy_load(self, item_count: int) -> bool:
        """Verifica se deve usar lazy loading"""
        return item_count > self.lazy_load_threshold
    
    def optimize_table_rendering(self, data: list, page_size: int = 50) -> list:
        """Otimiza renderização de tabelas grandes"""
        if len(data) <= page_size:
            return data
        
        # Retornar apenas primeira página
        return data[:page_size]
    
    def debounce_search(self, func: Callable, delay: float = 0.5):
        """Implementa debounce para buscas"""
        def decorator(*args, **kwargs):
            if hasattr(decorator, 'timer'):
                decorator.timer.cancel()
            
            decorator.timer = threading.Timer(delay, lambda: func(*args, **kwargs))
            decorator.timer.start()
        
        return decorator

class MemoryManager:
    """Gerenciador de memória"""
    
    def __init__(self):
        """Inicializa o gerenciador"""
        self.memory_threshold = 100 * 1024 * 1024  # 100MB
    
    def cleanup_unused_objects(self):
        """Limpa objetos não utilizados"""
        import gc
        collected = gc.collect()
        return collected
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Obtém uso de memória"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available
        }
    
    def should_cleanup(self) -> bool:
        """Verifica se deve fazer limpeza"""
        try:
            memory_usage = self.get_memory_usage()
            return memory_usage['rss'] > self.memory_threshold
        except:
            return False

class PerformanceOptimizer:
    """Otimizador geral de performance"""
    
    def __init__(self):
        """Inicializa o otimizador"""
        self.monitor = PerformanceMonitor()
        self.cache = CacheManager()
        self.db_optimizer = DatabaseOptimizer()
        self.ui_optimizer = UIOptimizer()
        self.memory_manager = MemoryManager()
        
        # Thread para limpeza automática
        self.cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def _periodic_cleanup(self):
        """Limpeza periódica automática"""
        while True:
            time.sleep(300)  # A cada 5 minutos
            
            try:
                # Limpeza de cache expirado
                self.cache.invalidate_cache()
                
                # Limpeza de memória se necessário
                if self.memory_manager.should_cleanup():
                    self.memory_manager.cleanup_unused_objects()
                
            except Exception as e:
                print(f"Erro na limpeza automática: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório completo de performance"""
        return {
            'metrics': self.monitor.get_metrics(),
            'cache_stats': self.cache.get_cache_stats(),
            'memory_usage': self.memory_manager.get_memory_usage(),
            'timestamp': datetime.now().isoformat()
        }
    
    def optimize_application(self):
        """Otimiza a aplicação como um todo"""
        # Limpeza de cache
        self.cache.invalidate_cache()
        
        # Limpeza de memória
        collected = self.memory_manager.cleanup_unused_objects()
        
        # Reset de métricas antigas
        self.monitor.reset_metrics()
        
        return {
            'cache_cleared': True,
            'objects_collected': collected,
            'metrics_reset': True
        }

# Instâncias globais
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()
performance_optimizer = PerformanceOptimizer()
