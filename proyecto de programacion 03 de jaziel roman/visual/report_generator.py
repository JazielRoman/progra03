# visual/report_generator.py

import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter       # type: ignore
from reportlab.pdfgen import canvas               # type: ignore
from reportlab.lib.units import inch              # type: ignore
from reportlab.lib.utils import ImageReader       # type: ignore

def generate_pdf_report(clients, orders, routes_freq, stats, filename="reporte.pdf"):
    """
    clients: lista de dicts con {ID, Name, TotalOrders}
    orders: lista de dicts con detalles de cada orden
    routes_freq: lista de (ruta_str, frecuencia)
    stats: dict con node_role_counts, origin_freq, dest_freq
    filename: salida
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - inch, "Informe de Simulación Drones")

    # 1. Tabla de Órdenes
    y = height - 1.5*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "1. Tabla de Órdenes")
    c.setFont("Helvetica", 10)
    y -= 0.3*inch
    headers = ["ID", "Cliente", "Origen", "Destino", "Status", "Costo"]
    x_positions = [inch, 1.5*inch, 3*inch, 4*inch, 5*inch, 6*inch]
    for i, h in enumerate(headers):
        c.drawString(x_positions[i], y, h)
    y -= 0.2*inch
    for o in orders:
        row = [
            str(o["OrderID"]), str(o["ClientID"]),
            str(o["Origen"]), str(o["Destino"]),
            o["Status"], str(o.get("Cost", ""))
        ]
        for i, cell in enumerate(row):
            c.drawString(x_positions[i], y, cell)
        y -= 0.2*inch
        if y < inch:
            c.showPage()
            y = height - inch

    # 2. Clientes con Más Pedidos
    c.showPage()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, height - inch, "2. Clientes con Más Pedidos")
    c.setFont("Helvetica", 10)
    y = height - 1.5*inch
    top_clients = sorted(clients, key=lambda c: c["TotalOrders"], reverse=True)
    for client in top_clients[:10]:
        c.drawString(inch, y,
                     f'Cliente {client["ID"]} ({client["Name"]}): {client["TotalOrders"]} pedidos')
        y -= 0.2*inch

    # 3. Rutas Más Frecuentes
    c.showPage()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, height - inch, "3. Rutas Más Frecuentes")
    c.setFont("Helvetica", 10)
    y = height - 1.5*inch
    for ruta, freq in routes_freq[:10]:
        c.drawString(inch, y, f'{ruta}: {freq} veces')
        y -= 0.2*inch

    # 4. Gráficas (roles)
    roles = stats["node_role_counts"]
    fig1, ax1 = plt.subplots()
    ax1.pie(roles.values(), labels=roles.keys(), autopct="%1.1f%%")
    ax1.axis("equal")
    imgdata = io.BytesIO()
    fig1.savefig(imgdata, format='PNG')
    plt.close(fig1)
    imgdata.seek(0)

    c.showPage()
    img_reader = ImageReader(imgdata)
    c.drawImage(img_reader, inch, height/2, width=4*inch, height=4*inch)

    # Finalizar y guardar
    c.save()
    buffer.seek(0)
    with open(filename, "wb") as f:
        f.write(buffer.read())

    return filename
