class Nodo:
    def __init__(self, elemento):
        """
        Inicializa un nodo con un elemento y un puntero siguiente (None por defecto).
        """
        self._element = elemento  # El valor o dato que almacena el nodo
        self._next = None         # Puntero al siguiente nodo (None indica fin de la lista)

    def __repr__(self):
        return f"Nodo({self._element})"  # Representación del nodo para imprimir
    
# Creando nodos
nodo1 = Nodo("LAX")
nodo2 = Nodo("MSP")
nodo3 = Nodo("ATL")
nodo4 = Nodo("BOS")

# Enlazando los nodos
nodo1._next = nodo2
nodo2._next = nodo3
nodo3._next = nodo4

# Imprimiendo la secuencia
nodo_actual = nodo1
while nodo_actual:
    print(nodo_actual._element, end=" -> ")
    nodo_actual = nodo_actual._next