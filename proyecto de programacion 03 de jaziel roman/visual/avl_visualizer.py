import matplotlib.pyplot as plt
import networkx as nx

class AVLVisualizer:
    @staticmethod
    def draw_avl_tree(edges):
        """
        edges: lista de tuplas (parent_key, child_key, 'L'|'R')
        Construye un grafo dirigido y devuelve la Figure para Streamlit.
        """
        G = nx.DiGraph()
        for parent, child, _ in edges:
            G.add_edge(parent, child)

        fig, ax = plt.subplots()
        # Usamos spring_layout en lugar de graphviz para evitar dependencia pygraphviz
        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            arrows=False,
            node_size=1000,
            font_size=10,
            ax=ax
        )
        ax.set_title("Árbol AVL de Rutas")
        ax.axis("off")
        return fig
