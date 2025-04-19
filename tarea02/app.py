# app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from models import *
from database import *
from lista_vuelos import *

# Crea las tablas en la base de datos si aún no existen
crear_base_datos()

app = FastAPI()
lista = ListaVuelos()

@app.post("/vuelos")
def crear_vuelo(
    codigo: str,
    estado: EstadoVuelo,
    hora: datetime,
    origen: str,
    destino: str,
    db: Session = Depends(get_db)
):
    # Crea y persiste el nuevo vuelo
    vuelo = Vuelo(
        codigo=codigo,
        estado=estado,
        hora=hora,
        origen=origen,
        destino=destino
    )
    db.add(vuelo)
    db.commit()
    db.refresh(vuelo)

    # Inserta en la lista con prioridad
    if estado == EstadoVuelo.emergencia:
        lista.insertar_al_frente(vuelo, db)
    else:
        lista.insertar_al_final(vuelo, db)

    return vuelo

@app.get("/vuelos/total")
def total_vuelos():
    return {"total": lista.longitud()}

@app.get("/vuelos/proximo")
def proximo_vuelo():
    v = lista.obtener_primero()
    if not v:
        raise HTTPException(status_code=404, detail="No hay vuelos pendientes")
    return v

@app.get("/vuelos/ultimo")
def ultimo_vuelo():
    v = lista.obtener_ultimo()
    if not v:
        raise HTTPException(status_code=404, detail="No hay vuelos en la cola")
    return v

@app.get("/vuelos/lista")
def listar_vuelos():
    return {"total": lista.longitud(), "vuelos": lista.listar_todos()}

@app.post("/vuelos/insertar")
def insertar_en_posicion(
    codigo: str,
    posicion: int,
    db: Session = Depends(get_db)
):
    vuelo = db.query(Vuelo).filter(Vuelo.codigo == codigo).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    lista.insertar_en_posicion(vuelo, posicion, db)
    return {"message": f"Vuelo {codigo} insertado en posición {posicion}"}

@app.delete("/vuelos/{posicion}")
def eliminar_vuelo(
    posicion: int,
    db: Session = Depends(get_db)
):
    try:
        vuelo = lista.eliminar_de_posicion(posicion, db)
    except IndexError:
        raise HTTPException(status_code=400, detail="Posición inválida")
    return {"message": f"Vuelo {vuelo.codigo} eliminado de la posición {posicion}"}

@app.patch("/vuelos/reordenar")
def reordenar_vuelo(
    origen: int,
    destino: int,
    db: Session = Depends(get_db)
):
    try:
        lista.reordenar(origen, destino, db)
    except IndexError:
        raise HTTPException(status_code=400, detail="Posiciones inválidas")
    return {"message": f"Vuelo movido de {origen} a {destino}"}

@app.post("/vuelos/undo")
def undo(db: Session = Depends(get_db)):
    try:
        lista.undo(db)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Undo no está implementado aún")
    return {"message": "Operación deshecha"}

@app.post("/vuelos/redo")
def redo(db: Session = Depends(get_db)):
    try:
        lista.redo(db)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Redo no está implementado aún")
    return {"message": "Operación rehecha"}
