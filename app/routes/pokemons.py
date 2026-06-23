from fastapi import APIRouter, Query, HTTPException, Request
from app.services.poke_service import get_pokemons_list, get_pokemon_by_id_or_name
from app.models import PaginatedPokemonResponse, PokemonResponse

router = APIRouter(prefix="/pokemons", tags=["Pokemons"])

@router.get("", response_model=PaginatedPokemonResponse)
async def list_pokemons(
    request: Request,
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0)
):
    """
    Lista os Pokémons de forma paginada consumindo os dados diretamente da PokéAPI.
    Retorna a lista de dados detalhados e os links dinâmicos de paginação.
    """
    result = await get_pokemons_list(limit, offset)
    total = result["total"]
    
    # Construção dos links dinâmicos de 'next' e 'previous' conforme exigido
    base_url = str(request.url_for("list_pokemons"))
    
    next_offset = offset + limit
    next_url = f"{base_url}?limit={limit}&offset={next_offset}" if next_offset < total else None
    
    prev_offset = offset - limit
    prev_url = f"{base_url}?limit={limit}&offset={prev_offset}" if prev_offset >= 0 else None

    return {
        "data": result["data"],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "next": next_url,
            "previous": prev_url
        }
    }

@router.get("/{id_or_name}", response_model=PokemonResponse)
async def get_pokemon(id_or_name: str):
    """
    Busca os detalhes de um Pokémon específico utilizando o ID ou o Nome.
    Trata automaticamente espaços em branco e letras maiúsculas na requisição.
    """
    # Tratamento direto do parâmetro para evitar erros de digitação (ex: 'Pikachu ' -> 'pikachu')
    cleaned_param = id_or_name.strip().lower()
    
    pokemon = await get_pokemon_by_id_or_name(cleaned_param)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")
    return pokemon