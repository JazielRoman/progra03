import datetime

class Order:
    def __init__(self,
                 order_id: int,
                 client_id: int,
                 origen_id: int,
                 destino_id: int,
                 status: str,
                 created_at: datetime.datetime,
                 prioridad: int):
        self.order_id = order_id
        self.client_id = client_id
        self.origen_id = origen_id
        self.destino_id = destino_id
        self.status = status            # 'pendiente', 'en ruta', 'completado'
        self.created_at = created_at
        self.prioridad = prioridad
        self.delivery_date = None       # se asigna al completar
        self.cost = None                # se asigna al completar

    def mark_as_completed(self, cost: int):
        self.status = 'completado'
        self.delivery_date = datetime.datetime.now()
        self.cost = cost

    def to_dict(self):
        return {
            "OrderID": self.order_id,
            "ClientID": self.client_id,
            "Origen": self.origen_id,
            "Destino": self.destino_id,
            "Status": self.status,
            "CreatedAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Priority": self.prioridad,
            "DeliveryDate": self.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if self.delivery_date else None,
            "Cost": self.cost
        }

    def __repr__(self):
        return (f"Order({self.order_id}, cli={self.client_id}, "
                f"orig={self.origen_id}, dest={self.destino_id}, "
                f"status={self.status})")
