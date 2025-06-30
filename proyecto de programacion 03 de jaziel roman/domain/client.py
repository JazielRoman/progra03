class Client:
    def __init__(self, client_id: int, name: str):
        self.client_id = client_id
        self.name = name
        self.total_orders = 0

    def increment_order_count(self):
        self.total_orders += 1

    def to_dict(self):
        return {
            "ID": self.client_id,
            "Name": self.name,
            "TotalOrders": self.total_orders
        }

    def __repr__(self):
        return f"Client({self.client_id}, name={self.name}, orders={self.total_orders})"
