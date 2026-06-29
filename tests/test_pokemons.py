import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# 1. Configuração de um banco de dados SQLite exclusivo para testes
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_pokemons.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


# 2. Fixture que prepara o banco de dados antes de cada teste e remove depois
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Cria as tabelas antes de cada teste e remove-as depois para garantir testes limpos e isolados."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


# 3. Fixture que injeta a sessão de teste nas rotas do FastAPI
@pytest.fixture(scope="function")
def client():
    """Substitui a dependência get_db da API pela sessão de testes e retorna o TestClient."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    # Aplica o override na aplicação FastAPI
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
        
    # Limpa os overrides após o teste finalizar
    app.dependency_overrides.clear()


# =============================================================================
# TESTES UNITÁRIOS REESCRITOS E AJUSTADOS COM AS ROTAS CORRETAS
# =============================================================================

def test_create_pokemon_local_success(client):
    """[POST] Testa a criação com sucesso de um Pokémon localmente"""
    pokemon_data = {
        "name": "Deletavel", 
        "height": 10, 
        "weight": 130, 
        "types": ["normal"], 
        "sprite_front": "http://example.com/front.png", 
        "sprite_back": "http://example.com/back.png"
    }
    response = client.post("/pokemons/local", json=pokemon_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "deletavel"  # A API aplica .lower() no nome


def test_create_duplicate_pokemon_local_error(client):
    """[POST ERRO] Testa erro ao tentar cadastrar o mesmo Pokémon duplicado"""
    pokemon_data = {
        "name": "Deletavel", "height": 10, "weight": 130, 
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    # Cria o primeiro
    client.post("/pokemons/local", json=pokemon_data)
    # Tenta criar o segundo idêntico
    response = client.post("/pokemons/local", json=pokemon_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Pokémon com este nome já está cadastrado no banco local."


def test_read_all_pokemons_local(client):
    """[GET] Testa a listagem de todos os Pokémons cadastrados localmente (/local/all)"""
    # Cadastra um Pokémon para garantir que a lista não retorne vazia
    pokemon_data = {
        "name": "Listavel", "height": 5, "weight": 50, 
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    client.post("/pokemons/local", json=pokemon_data)

    # Chamada corrigida para o endpoint correto: /pokemons/local/all
    response = client.get("/pokemons/local/all")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "listavel"


def test_read_specific_pokemon_local_by_id_and_name(client):
    """[GET] Testa a busca de um Pokémon local específico pelo ID ou Nome"""
    # Cadastra um Pokémon para obter um ID válido
    pokemon_data = {
        "name": "Pikachu Local", "height": 4, "weight": 60, 
        "types": ["electric"], "sprite_front": "a", "sprite_back": "b"
    }
    create_resp = client.post("/pokemons/local", json=pokemon_data)
    pokemon_id = create_resp.json()["id"]

    # 1. Testa a busca usando o ID
    response_by_id = client.get(f"/pokemons/local/{pokemon_id}")
    assert response_by_id.status_code == 200
    assert response_by_id.json()["name"] == "pikachu local"

    # 2. Testa a busca usando o Nome
    response_by_name = client.get("/pokemons/local/pikachu local")
    assert response_by_name.status_code == 200
    assert response_by_name.json()["id"] == pokemon_id


def test_read_pokemon_local_not_found_error(client):
    """[GET ERRO] Testa erro ao buscar um Pokémon inexistente no banco local"""
    response = client.get("/pokemons/local/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pokémon não encontrado no banco de dados local."


def test_update_pokemon_local_success(client):
    """[PUT] Testa a atualização de dados de um Pokémon existente"""
    # Cadastra o Pokémon inicial
    pokemon_data = {
        "name": "Antes", "height": 1, "weight": 1, 
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    create_resp = client.post("/pokemons/local", json=pokemon_data)
    pokemon_id = create_resp.json()["id"]

    # Dados que serão atualizados
    updated_data = {
        "name": "Depois", "height": 5, "weight": 5, 
        "types": ["normal", "flying"], "sprite_front": "new_a", "sprite_back": "new_b"
    }
    response = client.put(f"/pokemons/local/{pokemon_id}", json=updated_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "depois"
    assert data["height"] == 5


def test_update_pokemon_local_not_found_error(client):
    """[PUT ERRO] Testa erro ao tentar atualizar um Pokémon inexistente"""
    updated_data = {
        "name": "Inexistente", "height": 5, "weight": 5, 
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    response = client.put("/pokemons/local/999", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Não foi possível atualizar: Pokémon local não encontrado."


def test_delete_pokemon_local_success(client):
    """[DELETE] Remove fisicamente o registro de Pokémon do banco local"""
    # Cadastra o registro que será excluído
    pokemon_data = {
        "name": "Deletavel", "height": 1, "weight": 1, 
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    create_resp = client.post("/pokemons/local", json=pokemon_data)
    pokemon_id = create_resp.json()["id"]

    # Executa a remoção
    response = client.delete(f"/pokemons/local/{pokemon_id}")
    assert response.status_code == 204  # HTTP_204_NO_CONTENT não retorna corpo


def test_delete_pokemon_local_not_found_error(client):
    """[ERRO DELETE] Testa erro ao tentar remover um ID inexistente"""
    response = client.delete("/pokemons/local/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Não foi possível deletar: Pokémon local não encontrado."


def test_create_pokemon_local_invalid_data_type_error(client):
    """[POST ERRO 422] Testa a validação de dados ao enviar um tipo incorreto (height como texto)"""
    pokemon_data = {
        "name": "InvalidoTipo",
        "height": "altura_invalida",  # Deveria ser um inteiro (int)
        "weight": 130,
        "types": ["normal"],
        "sprite_front": "a",
        "sprite_back": "b"
    }
    response = client.post("/pokemons/local", json=pokemon_data)
    assert response.status_code == 422  # Erro de validação do Pydantic


def test_create_pokemon_local_missing_required_field_error(client):
    """[POST ERRO 422] Testa a validação de dados ao omitir um campo obrigatório (name)"""
    pokemon_data = {
        # "name" propositalmente ausente
        "height": 10,
        "weight": 130,
        "types": ["normal"],
        "sprite_front": "a",
        "sprite_back": "b"
    }
    response = client.post("/pokemons/local", json=pokemon_data)
    assert response.status_code == 422


def test_update_pokemon_local_invalid_data_type_error(client):
    """[PUT ERRO 422] Testa a validação de dados ao atualizar com um tipo incorreto (weight como texto)"""
    # Cadastra um Pokémon válido primeiro
    pokemon_data = {
        "name": "ParaAtualizar", "height": 10, "weight": 50,
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    create_resp = client.post("/pokemons/local", json=pokemon_data)
    pokemon_id = create_resp.json()["id"]

    # Tenta atualizar com um tipo de dado inválido
    invalid_update = {
        "name": "Atualizado", "height": 10, "weight": "peso_invalido",
        "types": ["normal"], "sprite_front": "a", "sprite_back": "b"
    }
    response = client.put(f"/pokemons/local/{pokemon_id}", json=invalid_update)
    assert response.status_code == 422