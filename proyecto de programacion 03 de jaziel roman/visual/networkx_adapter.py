import networkx as nx

class NetworkXAdapter:
    @staticmethod
    def graph_to_networkx(graph):
        """
        Convierte nuestro Graph a un objeto networkx.Graph,
        asignando atributo 'role' a cada nodo y 'weight' a cada arista.
        """
        G_nx = nx.Graph()
        for vid, vert in graph.vertices.items():
            G_nx.add_node(vid, role=vert.role)

        visited_edges = set()
        for src, neighbors in graph.adj.items():
            for dst, w in neighbors:
                if (dst, src) in visited_edges:
                    continue
                G_nx.add_edge(src, dst, weight=w)
                visited_edges.add((src, dst))
        return G_nx

    @staticmethod
    def get_node_colors(graph):
        """
        Devuelve lista de colores según rol de cada nodo
        en el mismo orden que graph.vertices.keys().
        """
        color_map = {
            'almacenamiento': 'green',
            'recarga': 'blue',
            'cliente': 'orange'
        }
        return [color_map[graph.vertices[vid].role] for vid in graph.vertices]

    @staticmethod
    def get_edge_labels(G_nx):
        """
        Devuelve diccionario {(u,v): weight} para usar con nx.draw_networkx_edge_labels.
        """
        return nx.get_edge_attributes(G_nx, 'weight')
