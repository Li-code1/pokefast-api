import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_pokemons_success():
    """Testa a listagem padrão de Pokémons"""
    response = client.get("/pokemons?limit=2&offset=0")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "pagination" in json_data
    assert json_data["pagination"]["limit"] == 2

def test_get_specific_pokemon_success():
    """Testa a busca de um pokémon existente (Pikachu ID: 25)"""
    response = client.get("/pokemons/25")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "pikachu"
    assert json_data["id"] == 25

def test_get_pokemon_not_found():
    """Testa erro de Pokémon inexistente"""
    response = client.get("/pokemons/pokemon-inexistente-9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon não encontrado"