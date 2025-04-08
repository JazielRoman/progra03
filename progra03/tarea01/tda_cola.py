# tda_cola.py
class ColaMisiones:
    def __init__(self):
        self._cola = []

    def enqueue(self, mission):
        """Añade la misión al final de la cola."""
        self._cola.append(mission)

    def dequeue(self):
        """Elimina y retorna la primera misión de la cola."""
        if self.is_empty():
            return None
        return self._cola.pop(0)

    def first(self):
        """Retorna la primera misión sin removerla."""
        if self.is_empty():
            return None
        return self._cola[0]

    def is_empty(self):
        """Verifica si la cola está vacía."""
        return len(self._cola) == 0

    def size(self):
        """Retorna la cantidad de misiones en la cola."""
        return len(self._cola)