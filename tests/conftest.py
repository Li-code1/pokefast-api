import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Fixture que roda automaticamente uma vez por sessão de testes.
    Cria a tabela 'my_pokemons' antes dos testes e remove-a no final.
    """
    # Cria todas as tabelas mapeadas no SQLAlchemy (incluindo o PokemonDB)
    Base.metadata.create_all(bind=engine)
    
    yield  # Aqui é onde os teus testes são executados
    
    # Opcional: Remove as tabelas após o fim de todos os testes para manter o banco limpo
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    """
    Fixture que fornece o TestClient do FastAPI para os ficheiros de testes.
    """
    with TestClient(app) as c:
        yield c