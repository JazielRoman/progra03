# api/main.py

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import datetime

from sim.simulation import Simulation
from domain.order import Order
from visual.report_generator import generate_pdf_report

app = FastAPI(title="Sistema Logístico Drones API")

@app.get("/ping")
def ping():
    return {"pong": "ok"}

# Inicializar la simulación
sim = Simulation()
sim.start_simulation(n_nodes=15, m_edges=20, n_orders=10)

class OrderCreate(BaseModel):
    client_id: int
    origen_id: int
    prioridad: int

@app.get("/clients/")
def get_clients():
    return [sim.clients_map.get(cid).to_dict() for cid in sim.clients_map.keys()]

@app.get("/orders/")
def get_orders():
    return [sim.orders_map.get(oid).to_dict() for oid in sim.orders_map.keys()]

@app.post("/orders/create/", response_model=dict)
def create_order(order: OrderCreate):
    """
    Crear una nueva orden pendiente.
    """
    existing_ids = list(sim.orders_map.keys())
    new_id = max(existing_ids) + 1 if existing_ids else 0

    new_order = Order(
        order_id=new_id,
        client_id=order.client_id,
        origen_id=order.origen_id,
        destino_id=order.client_id,
        status="pendiente",
        created_at=datetime.datetime.now(),
        prioridad=order.prioridad
    )
    sim.orders_map.put(new_id, new_order)
    return new_order.to_dict()

@app.post("/orders/complete/", response_model=dict)
def complete_order(order_id: int = Query(..., description="ID de la orden a completar")):
    """
    Marcar una orden existente como completada.
    """
    ord_obj = sim.orders_map.get(order_id)
    if not ord_obj:
        raise HTTPException(404, "Orden no encontrada")
    if ord_obj.status != "pendiente":
        raise HTTPException(400, "Estado inválido")

    ruta, costo = sim.calculate_route(ord_obj.origen_id, ord_obj.destino_id)
    sim.complete_delivery(order_id, ruta, costo)
    return sim.orders_map.get(order_id).to_dict()

@app.get("/routes/frequent/")
def get_frequent_routes():
    return sim.get_frequent_routes()

@app.get("/report/pdf/")
def download_report():
    clients = [c.to_dict() for c in sim.get_clients_list()]
    orders  = [o.to_dict() for o in sim.get_orders_list()]
    rutas   = sim.get_frequent_routes()
    stats   = sim.get_statistics()
    pdf_path = generate_pdf_report(clients, orders, rutas, stats, filename="reporte_api.pdf")
    return FileResponse(pdf_path, media_type="application/pdf", filename="reporte_api.pdf")

@app.on_event("startup")
async def list_routes():
    print("\n--- Registered routes: ---")
    for route in app.routes:
        print(f"{route.path}  {route.methods}")
    print("--------------------------\n")

print("🔥 Ejecutando desde:", __file__)
