# app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from models import *
from database import *
from lista_vuelos import *

# Crear tablas al iniciar
crear_base_datos()

app = FastAPI()
lista = ListaVuelos()

# Pydantic schema para insertar en posición
class InsertPos(BaseModel):
    codigo: str
    posicion: int

@app.post("/vuelos")
def crear_vuelo(
    codigo: str,
    estado: EstadoVuelo,
    hora: datetime,
    origen: str,
    destino: str,
    db: Session = Depends(get_db)
):
    # Asegurar que no se repite código
    if db.query(Vuelo).filter(Vuelo.codigo == codigo).first():
        raise HTTPException(400, f"Ya existe un vuelo con código {codigo}")
    
    vuelo = Vuelo(codigo=codigo, estado=estado, hora=hora, origen=origen, destino=destino)
    db.add(vuelo)
    db.commit()
    db.refresh(vuelo)

    # Usar una copia del vuelo fresco para insertar en la lista
    vuelo_lista = Vuelo(
        id=vuelo.id, codigo=vuelo.codigo, estado=vuelo.estado,
        hora=vuelo.hora, origen=vuelo.origen, destino=vuelo.destino
    )

    if estado == EstadoVuelo.emergencia:
        lista.insertar_al_frente(vuelo_lista, db)
    else:
        lista.insertar_al_final(vuelo_lista, db)
    
    return vuelo

@app.get("/vuelos/total")
def total_vuelos():
    return {"total": lista.longitud()}

@app.get("/vuelos/proximo")
def proximo_vuelo():
    v = lista.obtener_primero()
    if not v:
        raise HTTPException(404, "No hay vuelos pendientes")
    return v

@app.get("/vuelos/ultimo")
def ultimo_vuelo():
    v = lista.obtener_ultimo()
    if not v:
        raise HTTPException(404, "No hay vuelos en la cola")
    return v

@app.get("/vuelos/lista")
def listar_vuelos():
    return {"total": lista.longitud(), "vuelos": lista.listar_todos()}

@app.post("/vuelos/insertar")
def insertar_en_posicion(data: InsertPos, db: Session = Depends(get_db)):
    if data.posicion < 0:
        raise HTTPException(400, "La posición no puede ser negativa")

    vuelo = db.query(Vuelo).filter(Vuelo.codigo == data.codigo).first()
    if not vuelo:
        raise HTTPException(404, "Vuelo no encontrado")

    vuelo_lista = Vuelo(
        id=vuelo.id, codigo=vuelo.codigo, estado=vuelo.estado,
        hora=vuelo.hora, origen=vuelo.origen, destino=vuelo.destino
    )

    try:
        lista.insertar_en_posicion(vuelo_lista, data.posicion, db)
    except IndexError:
        raise HTTPException(400, "Posición fuera de rango")

    return {"message": f"Vuelo {data.codigo} insertado en posición {data.posicion}"}

@app.delete("/vuelos/{posicion}")
def eliminar_vuelo(posicion: int, db: Session = Depends(get_db)):
    try:
        vuelo = lista.eliminar_de_posicion(posicion, db)
    except IndexError:
        raise HTTPException(400, "Posición inválida")
    if vuelo:
        db.delete(vuelo)
        db.commit()
        return {"message": f"Vuelo {vuelo.codigo} eliminado tanto en lista como en BD"}
    raise HTTPException(404, "Vuelo no encontrado en la base de datos")

@app.patch("/vuelos/reordenar")
def reordenar_vuelo(origen: int, destino: int, db: Session = Depends(get_db)):
    try:
        lista.reordenar(origen, destino, db)
    except IndexError:
        raise HTTPException(400, "Posiciones inválidas")
    return {"message": f"Vuelo movido de {origen} a {destino}"}

@app.post("/vuelos/undo")
def undo(db: Session = Depends(get_db)):
    if not lista.undo(db):
        raise HTTPException(400, "No hay operaciones para deshacer")
    return {"message": "Operación deshecha"}

@app.post("/vuelos/redo")
def redo(db: Session = Depends(get_db)):
    if not lista.redo(db):
        raise HTTPException(400, "No hay operaciones para rehacer")
    return {"message": "Operación rehecha"}
