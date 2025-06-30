import random
import datetime
from model.graph import Graph
from domain.client import Client
from domain.order import Order
from tda.hashmap import HashMap

class SimulationInitializer:
    def __init__(self, n_nodes: int, m_edges: int, n_orders: int):
        self.n_nodes = n_nodes
        self.m_edges = m_edges
        self.n_orders = n_orders

        # 1. Generar grafo conectado
        self.graph = Graph()
        self.graph.generate_random_connected(n_nodes, m_edges)

        # 2. Separar nodos por rol
        self.storage_nodes = [vid for vid, v in self.graph.vertices.items() if v.role == 'almacenamiento']
        self.refuel_nodes  = [vid for vid, v in self.graph.vertices.items() if v.role == 'recarga']
        self.client_nodes  = [vid for vid, v in self.graph.vertices.items() if v.role == 'cliente']

        # 3. Crear clientes en un HashMap (client_id → Client)
        self.clients_map = HashMap()
        for cid in self.client_nodes:
            new_client = Client(cid, name=f"Cliente-{cid}")
            self.clients_map.put(cid, new_client)

        # 4. Crear órdenes iniciales en HashMap (order_id → Order)
        self.orders_map = HashMap()
        for i in range(n_orders):
            origen = random.choice(self.storage_nodes)
            destino = random.choice(self.client_nodes)
            prioridad = random.randint(1, 5)
            order_obj = Order(
                order_id = i,
                client_id = destino,
                origen_id = origen,
                destino_id = destino,
                status = 'pendiente',
                created_at = datetime.datetime.now(),
                prioridad = prioridad
            )
            self.orders_map.put(i, order_obj)

        # 5. Árbol AVL para registrar rutas frecuentes
        from tda.avl import AVLTree
        self.route_avl = AVLTree()

        # 6. Frecuencias de nodos (origen y destino)
        self.origin_freq = {}
        self.dest_freq = {}

    def get_initialized_data(self):
        """
        Devuelve tuplas con:
        - grafo,
        - mapa de clientes,
        - mapa de órdenes,
        - AVL de rutas,
        - diccionario origin_freq,
        - diccionario dest_freq.
        """
        return (self.graph,
                self.clients_map,
                self.orders_map,
                self.route_avl,
                self.origin_freq,
                self.dest_freq)
