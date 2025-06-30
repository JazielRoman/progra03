import sys
import os

# Subimos un nivel para que 'sim' y 'visual' estén en el path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import random
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from sim.simulation import Simulation
from visual.map.map_builder import MapBuilder
from visual.avl_visualizer import AVLVisualizer
from visual.report_generator import generate_pdf_report
from streamlit_folium import st_folium  # type: ignore
import folium  # type: ignore
from math import radians, sin, cos, sqrt, atan2

# ------------------------------------------------------------------
# Función para resumir información del vuelo según ruta y coordenadas
# ------------------------------------------------------------------
def summarize_flight(route, coords_map):
    total_distance_km = 0.0
    for i in range(len(route) - 1):
        lat1, lon1 = coords_map[route[i]]
        lat2, lon2 = coords_map[route[i + 1]]

        R = 6371  # Radio de la Tierra en km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        dist = R * c
        total_distance_km += dist

    estimated_speed_kmh = 50  # Velocidad ejemplo del drone en km/h
    estimated_time_h = total_distance_km / estimated_speed_kmh
    battery_used = total_distance_km * 1.1  # Consumo con margen de seguridad

    return {
        "total_distance_km": total_distance_km,
        "estimated_time_h": estimated_time_h,
        "battery_used": battery_used
    }

# ------------------------------------------------------------------
# Persistencia de la simulación, coords y última ruta calculada
# ------------------------------------------------------------------
if "sim" not in st.session_state:
    st.session_state.sim = Simulation()
if "last_route" not in st.session_state:
    st.session_state.last_route = None
sim = st.session_state.sim

st.set_page_config(page_title="Simulación Logística Drones", layout="wide")
st.title("✅ Sistema Logístico Autónomo con Drones")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Run Simulation",
    "2. Explore Network",
    "3. Clients & Orders",
    "4. Route Analytics",
    "5. General Statistics"
])

# -----------------------------------------------------
# Pestaña 1: Run Simulation
# -----------------------------------------------------
with tab1:
    st.header("Configuración e Inicio de la Simulación")

    n_nodes  = st.slider("Número de nodos", 10, 150, 15, key="n_nodes")
    m_edges  = st.slider("Número de aristas", n_nodes - 1, 300, 20, key="m_edges")
    n_orders = st.slider("Número de órdenes", 10, 500, 10, key="n_orders")

    st.write(f"✅ Aproximado: {int(n_nodes*0.2)} almacén, {int(n_nodes*0.2)} recarga, {n_nodes - int(n_nodes*0.4)} clientes.")

    if st.button("▶️ Start Simulation", key="start_sim"):
        if m_edges < n_nodes - 1:
            st.error("Aristas insuficientes para grafo conexo (>= n_nodes - 1).")
        else:
            sim.start_simulation(n_nodes, m_edges, n_orders)
            st.session_state.coords_map = {
                nid: (
                    -38.736946 + random.uniform(-0.01, 0.01),
                    -72.590378 + random.uniform(-0.01, 0.01)
                )
                for nid in sim.graph.vertices
            }
            st.session_state.last_route = None
            st.success("Simulación iniciada correctamente.")

# -----------------------------------------------------
# Pestaña 2: Explore Network
# -----------------------------------------------------
with tab2:
    st.header("Visualización Geoespacial y Cálculo de Rutas")

    if sim.graph is None:
        st.info("Inicia la simulación primero.")
    else:
        coords_map  = st.session_state.get("coords_map", {})
        origen_sel  = st.selectbox(
            "Nodo Origen (📦)",
            [nid for nid, v in sim.graph.vertices.items() if v.role == "almacenamiento"],
            key="origen_sel"
        )
        destino_sel = st.selectbox(
            "Nodo Destino (👤)",
            [nid for nid, v in sim.graph.vertices.items() if v.role == "cliente"],
            key="destino_sel"
        )
        algoritmo   = st.radio("Algoritmo", ["DFS", "Dijkstra", "Floyd-Warshall"], key="algoritmo")
        show_mst    = st.checkbox("Mostrar MST (Kruskal)", key="show_mst")
        calc        = st.button("✈ Calculate Route", key="calc_route")

        mb = MapBuilder(sim.graph)
        mb.add_nodes(coords_map)
        mb.add_edges(coords_map)

        if calc:
            # calculate_route ya registra en AVL internamente
            ruta, costo = sim.calculate_route(origen_sel, destino_sel)
            st.success(f"Ruta: {' → '.join(map(str, ruta))} | Costo: {costo}")
            info = summarize_flight(ruta, coords_map)
            st.markdown(f"""
**Resumen de Vuelo:**  
- Distancia: {info['total_distance_km']:.2f} km  
- Tiempo: {info['estimated_time_h']*60:.0f} min  
- Batería: {info['battery_used']:.2f} km
""")
            st.session_state.last_route = (origen_sel, destino_sel, ruta, costo)
            mb.highlight_route(ruta, coords_map)

        # Complete Delivery & Create Order
        if st.session_state.get("last_route") and st.button("✅ Complete Delivery and Create Order", key="complete_delivery"):
            origen_r, destino_r, ruta_r, costo_r = st.session_state.last_route
            found_id = None
            for oid in sim.orders_map.keys():
                ord_obj = sim.orders_map.get(oid)
                if ord_obj.origen_id == origen_r and ord_obj.destino_id == destino_r and ord_obj.status == "pendiente":
                    found_id = oid
                    break

            if found_id is not None:
                sim.complete_delivery(found_id, ruta_r, costo_r)
                st.success(f"Orden {found_id} completada y registrada en AVL.")
            else:
                st.warning("No hay orden pendiente para esos nodos.")
            st.session_state.last_route = None

        if show_mst:
            mb.show_mst(sim.graph.get_mst_kruskal(), coords_map)

        st_folium(mb.get_map(), width=700, height=500)

# -----------------------------------------------------
# Pestaña 3: Clients & Orders
# -----------------------------------------------------
with tab3:
    st.header("Listado de Clientes y Órdenes")
    if sim.graph is None:
        st.info("Inicia la simulación primero.")
    else:
        st.subheader("Clientes")
        st.json([c.to_dict() for c in sim.get_clients_list()])
        st.subheader("Órdenes")
        st.json([o.to_dict() for o in sim.get_orders_list()])

# -----------------------------------------------------
# Pestaña 4: Route Analytics
# -----------------------------------------------------
with tab4:
    st.header("Rutas Más Frecuentes y Árbol AVL")
    if sim.graph is None:
        st.info("Inicia la simulación primero.")
    else:
        rutas = sim.get_frequent_routes()
        if rutas:
            df = pd.DataFrame(rutas, columns=["Ruta", "Frecuencia"])
            st.dataframe(df)

            fig = AVLVisualizer.draw_avl_tree(sim.get_avl_tree_structure())
            st.pyplot(fig)

            if st.button("📄 Generar Informe PDF", key="gen_pdf"):
                clients = [c.to_dict() for c in sim.get_clients_list()]
                orders  = [o.to_dict() for o in sim.get_orders_list()]
                stats   = sim.get_statistics()
                pdf_path = generate_pdf_report(clients, orders, rutas, stats, filename="informe.pdf")
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=pdf_file,
                        file_name="informe_simulacion.pdf",
                        mime="application/pdf",
                        key="download_pdf"
                    )
        else:
            st.write("Aún no hay rutas registradas.")

# -----------------------------------------------------
# Pestaña 5: General Statistics
# -----------------------------------------------------
with tab5:
    st.header("Estadísticas Generales del Sistema")
    if sim.graph is None:
        st.info("Inicia la simulación primero.")
    else:
        stats  = sim.get_statistics()
        origin = stats["origin_freq"]
        if origin:
            df_o = pd.DataFrame([{"Nodo": n, "Visitas": f} for n, f in origin.items()]).set_index("Nodo")
            st.bar_chart(df_o["Visitas"])
        else:
            st.write("No hay datos de frecuencia de origen.")

        fig2, ax2 = plt.subplots()
        ax2.pie(
            stats["node_role_counts"].values(),
            labels=stats["node_role_counts"].keys(),
            autopct="%1.1f%%"
        )
        ax2.axis("equal")
        st.pyplot(fig2)
