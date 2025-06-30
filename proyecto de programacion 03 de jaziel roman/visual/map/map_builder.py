# visual/map/map_builder.py

import folium  # type: ignore
from folium import plugins  # type: ignore

class MapBuilder:
    def __init__(self, graph, center_coords=( -38.736946, -72.590378), zoom_start=13):
        """
        graph: instancia de model.Graph
        center_coords: lat/lon del centro del mapa (ej. Temuco)
        """
        self.graph = graph
        self.map = folium.Map(location=center_coords, zoom_start=zoom_start)
        # Colores por rol
        self.colors = {
            'almacenamiento': 'green',
            'recarga': 'blue',
            'cliente': 'orange'
        }

    def add_nodes(self, coords_map):
        """
        coords_map: dict {node_id: (lat, lon)}
        Dibuja un Marker por cada nodo.
        """
        for node_id, vertex in self.graph.vertices.items():
            lat, lon = coords_map[node_id]
            folium.CircleMarker(
                location=(lat, lon),
                radius=6,
                color=self.colors.get(vertex.role, 'gray'),
                fill=True,
                fill_opacity=0.8,
                popup=f"ID: {node_id}\nRol: {vertex.role}"
            ).add_to(self.map)

    def add_edges(self, coords_map):
        """
        Dibuja todas las aristas como líneas grises.
        """
        for u, neighbors in self.graph.adj.items():
            lat_u, lon_u = coords_map[u]
            for v, weight in neighbors:
                if u < v:
                    lat_v, lon_v = coords_map[v]
                    folium.PolyLine(
                        locations=[(lat_u, lon_u), (lat_v, lon_v)],
                        color='gray',
                        weight=2,
                        opacity=0.6,
                        tooltip=f"Peso: {weight}"
                    ).add_to(self.map)

    def highlight_route(self, path, coords_map, color='red'):
        """
        path: lista de node_ids en orden
        Dibuja la ruta resaltada en rojo con flechas.
        """
        points = [coords_map[n] for n in path]
        folium.PolyLine(
            locations=points,
            color=color,
            weight=4,
            opacity=0.8
        ).add_to(self.map)
        plugins.PolyLineTextPath(  # type: ignore
            folium.PolyLine(locations=points),
            '▶',
            repeat=True,
            offset=7,
            attributes={'fill': color, 'font-weight': 'bold', 'font-size': '12'}
        ).add_to(self.map)

    def show_mst(self, mst_edges, coords_map, color='purple'):
        """
        mst_edges: lista de (u, v, weight) devuelta por get_mst_kruskal()
        Dibuja el MST con líneas punteadas.
        """
        for u, v, w in mst_edges:
            lat_u, lon_u = coords_map[u]
            lat_v, lon_v = coords_map[v]
            folium.PolyLine(
                locations=[(lat_u, lon_u), (lat_v, lon_v)],
                color=color,
                weight=3,
                opacity=0.7,
                dash_array='5,10',
                tooltip=f"MST edge: {u}→{v}, peso {w}"
            ).add_to(self.map)

    def get_map(self):
        """
        Devuelve el objeto folium.Map (para incrustar en Streamlit).
        """
        return self.map
