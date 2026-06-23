from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class PokemonSprites(BaseModel):
    front_default: Optional[str] = None
    back_default: Optional[str] = None

class PokemonResponse(BaseModel):
    name: str
    id: int
    height: int
    weight: int
    types: List[str]
    sprites: PokemonSprites

class PaginationInfo(BaseModel):
    total: int
    limit: int
    offset: int
    next: Optional[str] = None
    previous: Optional[str] = None

class PaginatedPokemonResponse(BaseModel):
    data: List[PokemonResponse]
    pagination: PaginationInfo