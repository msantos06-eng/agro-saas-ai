from sqlalchemy import Column, Integer, String, ForeignKey, Float
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    usuario = Column(String, unique=True)
    senha = Column(String)

class Fazenda(Base):
    __tablename__ = "fazendas"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

class Talhao(Base):
    __tablename__ = "talhoes"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    area = Column(Float)
    fazenda_id = Column(Integer, ForeignKey("fazendas.id"))