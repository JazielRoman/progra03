# models.py
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class EstadoVuelo(str, enum.Enum):
    programado = "programado"
    emergencia = "emergencia"
    retrasado = "retrasado"

class Vuelo(Base):
    __tablename__ = "vuelos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, unique=True, nullable=False)
    estado = Column(Enum(EstadoVuelo), nullable=False)
    hora = Column(DateTime, default=datetime.utcnow)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)

    def __repr__(self):
        return f"<Vuelo {self.codigo} | {self.estado} | {self.hora}>"

class Nodo:
    def __init__(self, vuelo: Vuelo):
        self.vuelo = vuelo
        self.anterior = None
        self.siguiente = None
