from fastapi import FastAPI
from app.routes import pokemons

app = FastAPI(
    title="PokeFast API",
    description="Uma API RESTful paginada integrada à PokéAPI original.",
    version="1.0.0"
)

# Inclui as rotas modulares
app.include_router(pokemons.router)

@app.get("/")
async def root():
    return {"message": "PokeFast API está online! Acesse /docs para a documentação automatizada."}