import httpx
import os
import asyncio
import json
import redis
from typing import Dict, Any, Optional

# Configurações de Ambiente
POKEAPI_URL = os.getenv("POKEAPI_URL", "https://pokeapi.co/api/v2/pokemon/")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Inicialização do cliente Redis para Gerenciamento de Cache
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None

async def fetch_pokemon_detail(client: httpx.AsyncClient, url: str) -> Optional[Dict[str, Any]]:
    """
    Busca os detalhes de um Pokémon utilizando uma sessão compartilhada do cliente HTTP.
    Implementa cache estratégico via Redis para evitar requisições repetidas.
    """
    # Usar a própria URL ou o ID final dela como chave de cache única no Redis
    cache_key = f"poke_detail:{url}"
    
    # 1. Tenta buscar do cache primeiro
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            pass  # Evita que uma falha no Redis quebre a aplicação

    # 2. Se não estiver no cache, faz a requisição externa
    try:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            result = {
                "name": data["name"],
                "id": data["id"],
                "height": data["height"],
                "weight": data["weight"],
                "types": [t["type"]["name"] for t in data["types"]],
                "sprites": {
                    "front_default": data["sprites"]["front_default"],
                    "back_default": data["sprites"]["back_default"]
                }
            }
            
            # 3. Salva o resultado no Redis com expiração (TTL) de 1 hora (3600 segundos)
            if redis_client:
                try:
                    redis_client.setex(cache_key, 3600, json.dumps(result))
                except Exception:
                    pass
                    
            return result
    except Exception:
        return None
    return None

async def get_pokemons_list(limit: int, offset: int) -> Dict[str, Any]:
    """
    Busca a listagem paginada e resolve todos os detalhes dos Pokémons
    em paralelo utilizando asyncio.gather(), reduzindo drasticamente o tempo de resposta.
    """
    cache_list_key = f"poke_list:limit_{limit}:offset_{offset}"
    
    # Tenta obter a página completa direto do cache do Redis
    if redis_client:
        try:
            cached_list = redis_client.get(cache_list_key)
            if cached_list:
                return json.loads(cached_list)
        except Exception:
            pass

    async with httpx.AsyncClient() as client:
        # Busca a lista básica da PokéAPI
        response = await client.get(f"{POKEAPI_URL}?limit={limit}&offset={offset}")
        if response.status_code != 200:
            return {"data": [], "total": 0}
        
        base_data = response.json()
        total_count = base_data.get("count", 0)
        results = base_data.get("results", [])
        
        # MELHORIA: Criação e execução de todas as requisições em paralelo (asyncio.gather)
        # Passando o mesmo client reaproveita a conexão TCP (Connection Pooling)
        tasks = [fetch_pokemon_detail(client, item["url"]) for item in results]
        pokemon_details = await asyncio.gather(*tasks)
        
        # Filtra registros que eventualmente retornaram None por falha de rede
        filtered_details = [p for p in pokemon_details if p is not None]
        
        output = {
            "data": filtered_details,
            "total": total_count
        }
        
        # Salva o resultado da página no cache por 10 minutos
        if redis_client and filtered_details:
            try:
                redis_client.setex(cache_list_key, 600, json.dumps(output))
            except Exception:
                pass
                
        return output

async def get_pokemon_by_id_or_name(id_or_name: str) -> Optional[Dict[str, Any]]:
    """
    Busca um único Pokémon pelo seu ID ou Nome aplicando o tratamento normatizado de strings.
    """
    treated_name = id_or_name.strip().lower()
    url = f"{POKEAPI_URL}{treated_name}"
    
    async with httpx.AsyncClient() as client:
        return await fetch_pokemon_detail(client, url)
