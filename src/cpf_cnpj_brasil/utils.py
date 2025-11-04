"""Utilitários auxiliares para validação de CNPJ."""
import threading
import functools
from typing import Callable, Any
import time


def rate_limited(min_interval: float) -> Callable:
    """
    Decorator para garantir um intervalo mínimo entre chamadas de função.
    
    Thread-safe: Suporta uso em ambientes multi-threading.
    
    Parâmetros:
        min_interval (float): Intervalo mínimo em segundos entre chamadas.
    
    Retorna:
        Callable: Função decorada com controle de taxa.
    """
    def decorator(func: Callable) -> Callable:
        # Armazena o timestamp da última execução COMPLETA
        last_call_end = [0.0]  # Lista para permitir mutação em closure

        # Lock para garantir thread-safety
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with lock:  # Garante que apenas uma thread execute por vez
                current_time = time.time()
                time_since_last = current_time - last_call_end[0]

                # Se necessário, aguarda para respeitar o intervalo mínimo
                if time_since_last < min_interval:
                    wait_time = min_interval - time_since_last
                    time.sleep(wait_time)

            try:
                # Executa a função (fora do lock para permitir I/O)
                result = func(*args, **kwargs)
                return result
            finally:
                # Atualiza o timestamp APÓS a execução
                with lock:
                    last_call_end[0] = time.time()

        return wrapper
    return decorator
