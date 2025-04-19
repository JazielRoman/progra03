# models.py
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Integer
from sqlalchemy.orm import declarative_base  # CORREGIDO
import enum

# Declaración de la base para SQLAlchemy
Base = declarative_base()

# Enumeración para los estados del vuelo
class EstadoVuelo(str, enum.Enum):
    programado = "programado"
    emergencia = "emergencia"
    retrasado = "retrasado"

# Modelo ORM de la tabla "vuelos"
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

# Nodo para estructura de lista enlazada (no persiste en DB)
class Nodo:
    def __init__(self, vuelo: Vuelo):
        self.vuelo = vuelo
        self.anterior = None
        self.siguiente = None
