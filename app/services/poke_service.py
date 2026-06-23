import httpx
import os
from typing import Dict, Any, Optional

POKEAPI_URL = os.getenv("POKEAPI_URL", "https://pokeapi.co/api/v2/pokemon/")

async def fetch_pokemon_detail(url: str) -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
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
        except Exception:
            return None
    return None

async def get_pokemons_list(limit: int, offset: int) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        # Busca a lista paginada original
        response = await client.get(f"{POKEAPI_URL}?limit={limit}&offset={offset}")
        if response.status_code != 200:
            return {"data": [], "total": 0}
        
        base_data = response.json()
        total_count = base_data.get("count", 0)
        results = base_data.get("results", [])
        
        # Para cada pokémon retornado, busca os detalhes completos em paralelo
        pokemon_details = []
        for item in results:
            detail = await fetch_pokemon_detail(item["url"])
            if detail:
                pokemon_details.append(detail)
                
        return {
            "data": pokemon_details,
            "total": total_count
        }

async def get_pokemon_by_id_or_name(id_or_name: str) -> Optional[Dict[str, Any]]:
    url = f"{POKEAPI_URL}{id_or_name.lower()}"
    return await fetch_pokemon_detail(url)