class Vertex:
    def __init__(self, id: int, role: str):
        """
        id: identificador único (p. ej. entero 0, 1, 2, …).
        role: 'almacenamiento', 'recarga' o 'cliente'.
        visited: para recorridos DFS/BFS.
        """
        self.id = id
        self.role = role
        self.visited = False

    def __repr__(self):
        return f"Vertex({self.id}, role={self.role})"
