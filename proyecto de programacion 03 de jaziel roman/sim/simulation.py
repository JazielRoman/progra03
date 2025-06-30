# sim/simulation.py

import datetime
from domain.order import Order
from domain.client import Client

class Simulation:
    def __init__(self):
        self.graph = None
        self.clients_map = None    # HashMap de Client
        self.orders_map = None     # HashMap de Order
        self.route_avl = None
        self.origin_freq = None
        self.dest_freq = None
        self.max_battery = 50

    def start_simulation(self, n_nodes: int, m_edges: int, n_orders: int):
        initializer = __import__('sim.simulation_initializer', fromlist=['SimulationInitializer'])
        SI = getattr(initializer, 'SimulationInitializer')
        init_obj = SI(n_nodes, m_edges, n_orders)
        (self.graph,
         self.clients_map,
         self.orders_map,
         self.route_avl,
         self.origin_freq,
         self.dest_freq) = init_obj.get_initialized_data()

    def calculate_route(self, origen_id: int, destino_id: int):
        if self.graph is None:
            raise RuntimeError("Simulación no inicializada.")
        ruta, costo = self.graph.find_path_with_battery(origen_id, destino_id, self.max_battery)

        # Registro automático en AVL
        ruta_str = "→".join(str(n) for n in ruta)
        nodo_avl = self.route_avl.search(ruta_str)
        if nodo_avl is not None:
            nodo_avl.value += 1
        else:
            self.route_avl.insert(ruta_str, 1)

        if not ruta:
            raise RuntimeError("No se encontró ruta factible.")
        return ruta, costo

    def complete_delivery(self, order_id: int, ruta: list, costo_total: int):
        """
        Marca la orden como completada y actualiza el cliente.
        """
        # 1) Obtener la orden
        order_obj: Order = self.orders_map.get(order_id)
        if order_obj is None:
            raise ValueError(f"Orden {order_id} no existe.")

        # 2) Marcar como completada usando el método de la clase Order
        order_obj.mark_as_completed(costo_total)
        # Reinsertar para forzar persistencia en HashMap
        self.orders_map.put(order_id, order_obj)

        # 3) Actualizar contador del cliente
        client_obj: Client = self.clients_map.get(order_obj.client_id)
        if client_obj:
            client_obj.increment_order_count()
            # Reinsertar cliente actualizado
            self.clients_map.put(client_obj.client_id, client_obj)

        # 4) Actualizar estadísticas
        self.origin_freq[order_obj.origen_id]   = self.origin_freq.get(order_obj.origen_id, 0) + 1
        self.dest_freq[order_obj.destino_id]    = self.dest_freq.get(order_obj.destino_id, 0) + 1

    def get_clients_list(self):
        # Devolver la lista de objetos Client
        return [self.clients_map.get(cid) for cid in self.clients_map.keys()]

    def get_orders_list(self):
        # Devolver la lista de objetos Order
        return [self.orders_map.get(oid) for oid in self.orders_map.keys()]

    def get_frequent_routes(self):
        return self.route_avl.inorder_traversal()

    def get_avl_tree_structure(self):
        return self.route_avl.export_tree_as_edges()

    def get_statistics(self):
        stats = {
            'node_role_counts': {
                'almacenamiento': len([v for v in self.graph.vertices.values() if v.role == 'almacenamiento']),
                'recarga':       len([v for v in self.graph.vertices.values() if v.role == 'recarga']),
                'cliente':       len([v for v in self.graph.vertices.values() if v.role == 'cliente']),
            },
            'origin_freq': self.origin_freq,
            'dest_freq':   self.dest_freq
        }
        return stats
