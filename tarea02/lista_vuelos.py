from models import Nodo, Vuelo
from sqlalchemy.orm import Session

class ListaVuelos:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tam = 0
        self.undo_stack = []
        self.redo_stack = []

    def insertar_al_frente(self, vuelo: Vuelo, db: Session):
        nodo = Nodo(vuelo)
        if not self.cabeza:
            self.cabeza = self.cola = nodo
        else:
            nodo.siguiente = self.cabeza
            self.cabeza.anterior = nodo
            self.cabeza = nodo
        self.tam += 1
        self.undo_stack.append({"action": "insert_front", "vuelo": vuelo})
        self.redo_stack.clear()

    def insertar_al_final(self, vuelo: Vuelo, db: Session):
        nodo = Nodo(vuelo)
        if not self.cola:
            self.cabeza = self.cola = nodo
        else:
            self.cola.siguiente = nodo
            nodo.anterior = self.cola
            self.cola = nodo
        self.tam += 1
        self.undo_stack.append({"action": "insert_back", "vuelo": vuelo})
        self.redo_stack.clear()

    def insertar_en_posicion(self, vuelo: Vuelo, posicion: int, db: Session):
        if posicion < 0 or posicion > self.tam:
            raise IndexError("Posición fuera de rango")
        if posicion == 0:
            return self.insertar_al_frente(vuelo, db)
        if posicion == self.tam:
            return self.insertar_al_final(vuelo, db)

        actual = self.cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        nuevo = Nodo(vuelo)
        anterior = actual.anterior
        anterior.siguiente = nuevo
        nuevo.anterior = anterior
        nuevo.siguiente = actual
        actual.anterior = nuevo
        self.tam += 1
        self.undo_stack.append({"action": "insert_pos", "vuelo": vuelo, "pos": posicion})
        self.redo_stack.clear()

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
        vuelo = actual.vuelo

        # Eliminar referencias previas con el mismo código
        self.undo_stack = [
            op for op in self.undo_stack
            if not (op.get("vuelo") and op["vuelo"].codigo == vuelo.codigo)
        ]
        self.redo_stack = [
            op for op in self.redo_stack
            if not (op.get("vuelo") and op["vuelo"].codigo == vuelo.codigo)
        ]

        # Guardar solo los datos del vuelo (no el objeto)
        self.undo_stack.append({
            "action": "delete",
            "vuelo_data": {
                "codigo": vuelo.codigo,
                "estado": vuelo.estado,
                "hora": vuelo.hora,
                "origen": vuelo.origen,
                "destino": vuelo.destino
            },
            "pos": posicion
        })
        self.redo_stack.clear()
        return vuelo

    def obtener_primero(self):
        return self.cabeza.vuelo if self.cabeza else None

    def obtener_ultimo(self):
        return self.cola.vuelo if self.cola else None

    def longitud(self):
        return self.tam

    def listar_todos(self):
        result = []
        actual = self.cabeza
        while actual:
            v = actual.vuelo
            result.append({
                "codigo": v.codigo,
                "estado": v.estado,
                "hora": str(v.hora),
                "origen": v.origen,
                "destino": v.destino
            })
            actual = actual.siguiente
        return result

    def reordenar(self, origen: int, destino: int, db: Session):
        vuelo = self.eliminar_de_posicion(origen, db)
        self.insertar_en_posicion(vuelo, destino, db)
        self.undo_stack.append({"action": "reorder", "vuelo": vuelo, "src": origen, "dst": destino})
        self.redo_stack.clear()

    def undo(self, db: Session):
        if not self.undo_stack:
            return
        op = self.undo_stack.pop()
        a = op["action"]
        if a == "insert_front":
            self.eliminar_de_posicion(0, db)
        elif a == "insert_back":
            self.eliminar_de_posicion(self.tam - 1, db)
        elif a == "insert_pos":
            self.eliminar_de_posicion(op["pos"], db)
        elif a == "delete":
            data = op["vuelo_data"]
            vuelo = Vuelo(**data)
            self.insertar_en_posicion(vuelo, op["pos"], db)
        elif a == "reorder":
            self.reordenar(op["dst"], op["src"], db)
        self.redo_stack.append(op)

    def redo(self, db: Session):
        if not self.redo_stack:
            return
        op = self.redo_stack.pop()
        a = op["action"]
        if a == "insert_front":
            self.insertar_al_frente(op["vuelo"], db)
        elif a == "insert_back":
            self.insertar_al_final(op["vuelo"], db)
        elif a == "insert_pos":
            self.insertar_en_posicion(op["vuelo"], op["pos"], db)
        elif a == "delete":
            self.eliminar_de_posicion(op["pos"], db)
        elif a == "reorder":
            self.reordenar(op["src"], op["dst"], db)
        self.undo_stack.append(op)