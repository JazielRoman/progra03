class Route:
    def __init__(self, path: list, cost: int):
        self.path = path
        self.cost = cost

    def as_str(self):
        return "→".join(str(n) for n in self.path)

    def to_dict(self):
        return {
            "Path": self.as_str(),
            "Cost": self.cost
        }

    def __repr__(self):
        return f"Route(path={self.as_str()}, cost={self.cost})"
