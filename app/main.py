from fastapi import FastAPI
from app.routes import pokemons

# Importações necessárias para inicializar o banco de dados relacional
from app.database import engine, Base
import app.models  # Força o carregamento dos modelos para o SQLAlchemy mapear

# Cria as tabelas estruturadas do banco SQLite local automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PokeFast API",
    description="Uma API RESTful paginada integrada à PokéAPI original com suporte a CRUD local e persistência em SQLite.",
    version="1.0.0"
)

# Inclui as rotas modulares (Contendo a PokéAPI externa e o CRUD Local)
app.include_router(pokemons.router)

@app.get("/")
async def root():
    """
    Endpoint raiz indicando o status operacional da API e o suporte ao CRUD.
    """
    return {
        "message": "PokeFast API está online com CRUD e SQLite! Acesse /docs para a documentação automatizada."
    }
