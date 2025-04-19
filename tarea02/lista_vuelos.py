# lista_vuelos.py
from models import Nodo, Vuelo
from sqlalchemy.orm import Session

class ListaVuelos:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tam = 0
        self.historial_undo = []
        self.historial_redo = []

    def insertar_al_frente(self, vuelo: Vuelo, db: Session):
        nodo = Nodo(vuelo=vuelo)
        if not self.cabeza:
            self.cabeza = self.cola = nodo
        else:
            nodo.siguiente = self.cabeza
            self.cabeza.anterior = nodo
            self.cabeza = nodo
        self.tam += 1
        self.historial_undo.append(("eliminar_de_posicion", 0))
        self.historial_redo.clear()

    def insertar_al_final(self, vuelo: Vuelo, db: Session):
        nodo = Nodo(vuelo=vuelo)
        if not self.cola:
            self.cabeza = self.cola = nodo
        else:
            self.cola.siguiente = nodo
            nodo.anterior = self.cola
            self.cola = nodo
        self.tam += 1
        self.historial_undo.append(("eliminar_de_posicion", self.tam - 1))
        self.historial_redo.clear()

    def insertar_en_posicion(self, vuelo: Vuelo, posicion: int, db: Session):
        if posicion < 0 or posicion > self.tam:
            raise IndexError("Posición fuera de rango")
        if posicion == 0:
            return self.insertar_al_frente(vuelo, db)
        if posicion == self.tam:
            return self.insertar_al_final(vuelo, db)

        nuevo = Nodo(vuelo=vuelo)
        actual = self.cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        anterior = actual.anterior

        anterior.siguiente = nuevo
        nuevo.anterior = anterior
        nuevo.siguiente = actual
        actual.anterior = nuevo
        self.tam += 1
        self.historial_undo.append(("eliminar_de_posicion", posicion))
        self.historial_redo.clear()

    def eliminar_de_posicion(self, posicion: int, db: Session):
        if posicion < 0 or posicion >= self.tam:
            raise IndexError("Posición fuera de rango")
        actual = self.cabeza
        for _ in range(posicion):
            actual = actual.siguiente

        if actual.anterior:
            actual.anterior.siguiente = actual.siguiente
        else:
            self.cabeza = actual.siguiente

        if actual.siguiente:
            actual.siguiente.anterior = actual.anterior
        else:
            self.cola = actual.anterior

        self.tam -= 1
        self.historial_undo.append(("insertar_en_posicion", actual.vuelo, posicion))
        self.historial_redo.clear()
        return actual.vuelo

    def obtener_primero(self):
        return self.cabeza.vuelo if self.cabeza else None

    def obtener_ultimo(self):
        return self.cola.vuelo if self.cola else None

    def longitud(self):
        return self.tam

    def listar_todos(self):
        vuelos = []
        actual = self.cabeza
        while actual:
            vuelos.append({
                "codigo": actual.vuelo.codigo,
                "estado": actual.vuelo.estado,
                "hora": str(actual.vuelo.hora),
                "origen": actual.vuelo.origen,
                "destino": actual.vuelo.destino
            })
            actual = actual.siguiente
        return vuelos

    def reordenar(self, origen: int, destino: int, db: Session):
        vuelo = self.eliminar_de_posicion(origen, db)
        self.insertar_en_posicion(vuelo, destino, db)
        self.historial_undo.append(("reordenar", destino, origen))
        self.historial_redo.clear()

    def undo(self, db: Session):
        if not self.historial_undo:
            raise NotImplementedError("No hay operaciones para deshacer")
        accion = self.historial_undo.pop()
        if accion[0] == "eliminar_de_posicion":
            self.eliminar_de_posicion(accion[1], db)
            self.historial_redo.append(("insertar_en_posicion", accion[1]))
        elif accion[0] == "insertar_en_posicion":
            self.insertar_en_posicion(accion[1], accion[2], db)
            self.historial_redo.append(("eliminar_de_posicion", accion[2]))
        elif accion[0] == "reordenar":
            self.reordenar(accion[1], accion[2], db)
            self.historial_redo.append(("reordenar", accion[2], accion[1]))

    def redo(self, db: Session):
        if not self.historial_redo:
            raise NotImplementedError("No hay operaciones para rehacer")
        accion = self.historial_redo.pop()
        if accion[0] == "eliminar_de_posicion":
            self.eliminar_de_posicion(accion[1], db)
            self.historial_undo.append(("insertar_en_posicion", accion[1]))
        elif accion[0] == "insertar_en_posicion":
            self.insertar_en_posicion(accion[1], accion[2], db)
            self.historial_undo.append(("eliminar_de_posicion", accion[2]))
        elif accion[0] == "reordenar":
            self.reordenar(accion[1], accion[2], db)
            self.historial_undo.append(("reordenar", accion[2], accion[1]))