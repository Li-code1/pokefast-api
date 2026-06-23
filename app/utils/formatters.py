def clean_pokemon_name(name: str) -> str:
    """Remove espaços em branco e transforma o nome do Pokémon em minúsculas"""
    return name.strip().lower()