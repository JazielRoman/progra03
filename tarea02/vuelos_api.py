from fastapi import APIRouter, HTTPException
from typing import List
from models import *
from lista_vuelos import *

router = APIRouter()
lista_vuelos = ListaVuelos()

@router.post("/vuelos")
def crear_vuelo(vuelo: Vuelo):
    if vuelo.estado == EstadoVuelo.emergencia:
        lista_vuelos.insertar_al_frente(vuelo)
    else:
        lista_vuelos.insertar_al_final(vuelo)
    return {"mensaje": "Vuelo agregado correctamente"}

@router.get("/vuelos/total")
def obtener_total_vuelos():
    return {"total": lista_vuelos.longitud()}

@router.get("/vuelos/proximo")
def obtener_proximo_vuelo():
    vuelo = lista_vuelos.obtener_primero()
    if vuelo is None:
        raise HTTPException(status_code=404, detail="No hay vuelos en la lista")
    return vuelo

@router.get("/vuelos/ultimo")
def obtener_ultimo_vuelo():
    vuelo = lista_vuelos.obtener_ultimo()
    if vuelo is None:
        raise HTTPException(status_code=404, detail="No hay vuelos en la lista")
    return vuelo

@router.post("/vuelos/insertar")
def insertar_en_posicion(vuelo: Vuelo, posicion: int):
    try:
        lista_vuelos.insertar_en_posicion(vuelo, posicion)
        return {"mensaje": f"Vuelo insertado en la posición {posicion}"}
    except IndexError:
        raise HTTPException(status_code=400, detail="Posición inválida")

@router.delete("/vuelos/{posicion}")
def eliminar_vuelo(posicion: int):
    try:
        vuelo_eliminado = lista_vuelos.extraer_de_posicion(posicion)
        return {"mensaje": f"Vuelo {vuelo_eliminado.codigo} eliminado correctamente"}
    except IndexError:
        raise HTTPException(status_code=404, detail="No existe vuelo en esa posición")

@router.get("/vuelos/lista")
def obtener_lista_completa():
    return lista_vuelos.obtener_todos()

@router.patch("/vuelos/reordenar")
def reordenar_vuelo(posicion_actual: int, nueva_posicion: int):
    try:
        vuelo = lista_vuelos.extraer_de_posicion(posicion_actual)
        lista_vuelos.insertar_en_posicion(vuelo, nueva_posicion)
        return {"mensaje": f"Vuelo reordenado de {posicion_actual} a {nueva_posicion}"}
    except IndexError:
        raise HTTPException(status_code=400, detail="Posición inválida")