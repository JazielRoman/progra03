# app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Mision, Personaje, MisionPersonaje
from database import get_db
from tda_cola import ColaMisiones

app = FastAPI()
cola = ColaMisiones()  # Instanciamos la cola en memoria

@app.post("/personajes")
def crear_personaje(nombre: str, db: Session = Depends(get_db)):
    personaje = Personaje(nombre=nombre)
    db.add(personaje)
    db.commit()
    db.refresh(personaje)
    return personaje

@app.post("/misiones")
def crear_mision(nombre: str, descripcion: str, experiencia: int, db: Session = Depends(get_db)):
    mision = Mision(nombre=nombre, descripcion=descripcion, experiencia=experiencia, estado='pendiente')
    db.add(mision)
    db.commit()
    db.refresh(mision)
    return mision

@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    ultimo = db.query(MisionPersonaje).filter(MisionPersonaje.personaje_id == personaje_id)\
                .order_by(MisionPersonaje.orden.desc()).first()
    nuevo_orden = (ultimo.orden + 1) if ultimo else 1

    relacion = MisionPersonaje(
        personaje_id=personaje_id,
        mision_id=mision_id,
        orden=nuevo_orden
    )
    db.add(relacion)
    db.commit()
    cola.enqueue(relacion)  # Encolamos la misión en la cola
    return {"message": "Misión aceptada y encolada", "orden": nuevo_orden}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    relacion = db.query(MisionPersonaje)\
                .filter(MisionPersonaje.personaje_id == personaje_id)\
                .order_by(MisionPersonaje.orden.asc()).first()

    if not relacion:
        raise HTTPException(status_code=404, detail="No hay misiones pendientes")

    mision = relacion.mision
    if mision.estado != 'pendiente':
        raise HTTPException(status_code=400, detail="La misión ya está completada")

    mision.estado = 'completada'
    personaje = relacion.personaje
    personaje.experiencia += mision.experiencia

    db.delete(relacion)
    db.commit()
    cola.dequeue()  # Desencolamos la misión después de completarla
    return {"message": "Misión completada", "experiencia_total": personaje.experiencia}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    relaciones = db.query(MisionPersonaje)\
                   .filter(MisionPersonaje.personaje_id == personaje_id)\
                   .order_by(MisionPersonaje.orden.asc()).all()

    personaje = db.query(Personaje).filter(Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    return {
        "personaje": personaje.nombre,
        "misiones": [{"orden": r.orden, "mision_id": r.mision_id, "nombre": r.mision.nombre,
                      "estado": r.mision.estado} for r in relaciones]
    }
