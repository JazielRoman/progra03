import random
import heapq
from .vertex import Vertex

class Graph:
    def __init__(self):
        self.vertices = {}  # {id: Vertex}
        self.adj = {}       # {id: [(neighbor_id, weight), ...]}
        self.floyd_dist = None
        self.floyd_next = None

    def add_vertex(self, vertex: Vertex):
        if vertex.id in self.vertices:
            raise ValueError(f"Vertex {vertex.id} already exists.")
        self.vertices[vertex.id] = vertex
        self.adj[vertex.id] = []

    def add_edge(self, src: int, dst: int, weight: int):
        if src not in self.vertices or dst not in self.vertices:
            raise ValueError("Source or destination does not exist.")
        self.adj[src].append((dst, weight))
        self.adj[dst].append((src, weight))

    def get_neighbors(self, vertex_id: int):
        return self.adj.get(vertex_id, [])

    def reset_visits(self):
        for v in self.vertices.values():
            v.visited = False

    def generate_random_connected(self, n_nodes: int, m_edges: int):
        # 1. Crear vértices y asignar roles
        roles = ['almacenamiento'] * int(n_nodes * 0.2) + ['recarga'] * int(n_nodes * 0.2)
        roles += ['cliente'] * (n_nodes - len(roles))
        random.shuffle(roles)

        for i in range(n_nodes):
            v = Vertex(i, roles[i])
            self.add_vertex(v)

        # 2. Spanning tree para garantizar conectividad
        nodes = list(self.vertices.keys())
        random.shuffle(nodes)
        for i in range(1, n_nodes):
            a = nodes[i]
            b = random.choice(nodes[:i])
            w = random.randint(1, 10)
            self.add_edge(a, b, w)

        # 3. Agregar aristas restantes
        current_edges = sum(len(lst) for lst in self.adj.values()) // 2
        while current_edges < m_edges:
            a, b = random.sample(nodes, 2)
            if not any(nei == b for nei, _ in self.adj[a]):
                w = random.randint(1, 10)
                self.add_edge(a, b, w)
                current_edges += 1

    def find_path_with_battery(self, origen: int, destino: int, max_battery: int):
        self.reset_visits()
        best_route = []
        best_cost = float('inf')

        def dfs(current, battery_rest, cost_acc, path):
            nonlocal best_route, best_cost
            if cost_acc >= best_cost:
                return
            if current == destino:
                best_route = path.copy()
                best_cost = cost_acc
                return

            self.vertices[current].visited = True
            if self.vertices[current].role == 'recarga':
                battery_rest = max_battery

            for neighbor, w in self.get_neighbors(current):
                if not self.vertices[neighbor].visited and battery_rest >= w:
                    path.append(neighbor)
                    dfs(neighbor, battery_rest - w, cost_acc + w, path)
                    path.pop()

            self.vertices[current].visited = False

        dfs(origen, max_battery, 0, [origen])
        return best_route, best_cost

    # ─────────────────────────────────────
    # Algoritmo de Dijkstra
    def dijkstra(self, origen: int):
        dist = {v: float('inf') for v in self.vertices}
        prev = {v: None for v in self.vertices}
        dist[origen] = 0
        pq = [(0, origen)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, weight in self.get_neighbors(u):
                alt = dist[u] + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))
        return dist, prev

    # ─────────────────────────────────────
    # Algoritmo de Floyd-Warshall
    def floyd_warshall(self):
        n = len(self.vertices)
        INF = float('inf')
        dist = [[INF] * n for _ in range(n)]
        next_node = [[None] * n for _ in range(n)]

        for i in self.vertices:
            dist[i][i] = 0
            next_node[i][i] = i

        for u in self.adj:
            for v, w in self.adj[u]:
                dist[u][v] = w
                next_node[u][v] = v

        for k in self.vertices:
            for i in self.vertices:
                for j in self.vertices:
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]

        self.floyd_dist = dist
        self.floyd_next = next_node

    def get_floyd_path(self, origen: int, destino: int):
        if self.floyd_next is None:
            raise RuntimeError("Floyd-Warshall aún no ha sido ejecutado.")

        if self.floyd_next[origen][destino] is None:
            return [], float('inf')

        path = [origen]
        while origen != destino:
            origen = self.floyd_next[origen][destino]
            path.append(origen)

        cost = self.floyd_dist[path[0]][path[-1]]
        return path, cost

    # ─────────────────────────────────────
    # Algoritmo de Kruskal
    def get_mst_kruskal(self):
        parent = {}
        rank = {}

        def find(v):
            if parent[v] != v:
                parent[v] = find(parent[v])
            return parent[v]

        def union(u, v):
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                if rank[root_u] < rank[root_v]:
                    parent[root_u] = root_v
                else:
                    parent[root_v] = root_u
                    if rank[root_u] == rank[root_v]:
                        rank[root_u] += 1

        for v in self.vertices:
            parent[v] = v
            rank[v] = 0

        edges = []
        for u in self.adj:
            for v, w in self.adj[u]:
                if u < v:
                    edges.append((w, u, v))
        edges.sort()

        mst = []
        for w, u, v in edges:
            if find(u) != find(v):
                union(u, v)
                mst.append((u, v, w))

        return mst
