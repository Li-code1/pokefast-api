from fastapi import APIRouter, Query, HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict

# Importações dos seus Serviços e Esquemas Pydantic originais
from app.services.poke_service import get_pokemons_list, get_pokemon_by_id_or_name
from app.models import PaginatedPokemonResponse, PokemonResponse

# Novas Importações para a Persistência de Dados (SQLAlchemy)
from app.database import get_db
from app.models.pokemon import PokemonDB
from pydantic import BaseModel

router = APIRouter(prefix="/pokemons", tags=["Pokemons"])

# --- ESQUEMAS PYDANTIC AUXILIARES PARA O CRUD LOCAL ---
class PokemonLocalCreate(BaseModel):
    name: str
    height: int
    weight: int
    types: List[str]
    sprite_front: str
    sprite_back: str

class PokemonLocalResponse(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    types: str
    sprite_front: str
    sprite_back: str
    
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# 1. ENDPOINTS - CONSUMO DA POKEAPI EXTERNA
# ==============================================================================

@router.get("", response_model=PaginatedPokemonResponse)
async def list_pokemons(
    request: Request,
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0)
):
    """
    Lista os Pokémons de forma paginada consumindo os dados diretamente da PokéAPI.
    Otimizado para processamento em paralelo (asyncio.gather) e cache via Redis.
    """
    result = await get_pokemons_list(limit, offset)
    total = result["total"]
    
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


# ==============================================================================
# 2. ENDPOINTS - CRUD COMPLETO NO BANCO DE DADOS LOCAL (SQLALCHEMY)
# ==============================================================================

@router.post("/local", response_model=PokemonLocalResponse, status_code=status.HTTP_201_CREATED)
def create_pokemon_local(pokemon: PokemonLocalCreate, db: Session = Depends(get_db)):
    """
    [CREATE] Cria e persiste um novo Pokémon customizado no banco de dados SQLite local.
    """
    cleaned_name = pokemon.name.strip().lower()
    
    db_exists = db.query(PokemonDB).filter(PokemonDB.name == cleaned_name).first()
    if db_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Pokémon com este nome já está cadastrado no banco local."
        )
        
    db_pokemon = PokemonDB(
        name=cleaned_name,
        height=pokemon.height,
        weight=pokemon.weight,
        types=",".join(pokemon.types),
        sprite_front=pokemon.sprite_front,
        sprite_back=pokemon.sprite_back
    )
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

@router.get("/local/all", response_model=List[PokemonLocalResponse])
def read_all_pokemons_local(db: Session = Depends(get_db)):
    """
    [READ ALL] Lista todos os registros de Pokémons gravados no repositório local.
    """
    return db.query(PokemonDB).all()

@router.get("/local/{id_or_name}", response_model=PokemonLocalResponse)
def read_pokemon_local(id_or_name: str, db: Session = Depends(get_db)):
    """
    [READ BY ID/NAME LOCAL] Consulta detalhada no banco próprio.
    """
    cleaned_param = id_or_name.strip().lower()
    
    if cleaned_param.isdigit():
        db_pokemon = db.query(PokemonDB).filter(PokemonDB.id == int(cleaned_param)).first()
    else:
        db_pokemon = db.query(PokemonDB).filter(PokemonDB.name == cleaned_param).first()
        
    if not db_pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Pokémon não encontrado no banco de dados local."
        )
    return db_pokemon

@router.put("/local/{pokemon_id}", response_model=PokemonLocalResponse)
def update_pokemon_local(pokemon_id: int, pokemon: PokemonLocalCreate, db: Session = Depends(get_db)):
    """
    [UPDATE] Atualiza de forma completa as propriedades de um registro existente pelo ID.
    """
    db_pokemon = db.query(PokemonDB).filter(PokemonDB.id == pokemon_id).first()
    if not db_pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Não foi possível atualizar: Pokémon local não encontrado."
        )
        
    db_pokemon.name = pokemon.name.strip().lower()
    db_pokemon.height = pokemon.height
    db_pokemon.weight = pokemon.weight
    db_pokemon.types = ",".join(pokemon.types)
    db_pokemon.sprite_front = pokemon.sprite_front
    db_pokemon.sprite_back = pokemon.sprite_back
    
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

@router.delete("/local/{pokemon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pokemon_local(pokemon_id: int, db: Session = Depends(get_db)):
    """
    [DELETE] Remove fisicamente o registro de Pokémon do banco de dados SQLite local.
    """
    db_pokemon = db.query(PokemonDB).filter(PokemonDB.id == pokemon_id).first()
    if not db_pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Não foi possível deletar: Pokémon local não encontrado."
        )
    db.delete(db_pokemon)
    db.commit()
    return None


# ==============================================================================
# 3. RETORNO DA ROTA ORIGINAL ESPERADA PELOS TESTES UNITÁRIOS
# ==============================================================================

@router.get("/{id_or_name}", response_model=PokemonResponse)
async def get_pokemon(id_or_name: str):
    """
    Busca os detalhes de um Pokémon específico utilizando o ID ou o Nome na PokéAPI externa.
    Posicionado ao final para não interceptar as chamadas dos endpoints '/local'.
    """
    cleaned_param = id_or_name.strip().lower()
    
    pokemon = await get_pokemon_by_id_or_name(cleaned_param)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon não encontrado")
    return pokemon
