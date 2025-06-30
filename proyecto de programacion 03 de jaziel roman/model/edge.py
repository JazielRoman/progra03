class Edge:
    def __init__(self, src: int, dst: int, weight: int):
        """
        src: identificador del vértice origen.
        dst: identificador del vértice destino.
        weight: costo energético (1..10).
        """
        self.src = src
        self.dst = dst
        self.weight = weight

    def __repr__(self):
        return f"Edge({self.src} -> {self.dst}, w={self.weight})"
