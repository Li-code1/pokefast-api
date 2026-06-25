from sqlalchemy import Column, Integer, String
from app.database import Base

class PokemonDB(Base):
    __tablename__ = "my_pokemons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    height = Column(Integer)
    weight = Column(Integer)
    types = Column(String)  # Armazena os tipos separados por vírgula (ex: "grass,poison")
    sprite_front = Column(String)
    sprite_back = Column(String)
