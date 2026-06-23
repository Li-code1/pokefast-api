from celery_app import celery_app
import httpx
import json
import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

@celery_app.task(name="tasks.cache_pokemon_details")
def cache_pokemon_details(pokemon_name_or_id: str, data: dict):
    """Salva os detalhes do pokémon no Redis para evitar requisições repetidas à PokeAPI"""
    key = f"pokemon:{str(pokemon_name_or_id).lower()}"
    redis_client.setex(key, 3600, json.dumps(data)) # Cache expira em 1 hora
    return f"Pokemon {pokemon_name_or_id} salvo no cache."