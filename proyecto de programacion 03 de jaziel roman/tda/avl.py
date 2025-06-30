class AVLNode:
    def __init__(self, key: str, value: int):
        self.key = key
        self.value = value
        self.height = 1
        self.left = None
        self.right = None

    def __repr__(self):
        return f"({self.key}: {self.value}, h={self.height})"

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, key: str, value: int):
        """
        Inserta (key, value). Si key ya existe, sobrescribe value.
        """
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key: str, value: int):
        if node is None:
            return AVLNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Si existe, simplemente actualizamos el valor
            node.value = value
            return node

        # Actualizar altura y balancear
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Caso Left-Left
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)
        # Caso Right-Right
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)
        # Caso Left-Right
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # Caso Right-Left
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key: str):
        return self._search(self.root, key)

    def _search(self, node, key: str):
        if node is None:
            return None
        if key == node.key:
            return node
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def inorder_traversal(self):
        """
        Devuelve lista de (key, value) ordenada lexicográficamente por key.
        """
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if not node:
            return
        self._inorder(node.left, result)
        result.append((node.key, node.value))
        self._inorder(node.right, result)

    def export_tree_as_edges(self):
        """
        Devuelve lista de triples (parent_key, child_key, 'L'|'R') para graficar.
        """
        edges = []
        def dfs(node):
            if not node:
                return
            if node.left:
                edges.append((node.key, node.left.key, 'L'))
                dfs(node.left)
            if node.right:
                edges.append((node.key, node.right.key, 'R'))
                dfs(node.right)
        dfs(self.root)
        return edges

    # Métodos auxiliares
    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return (self._get_height(node.left) - self._get_height(node.right)) if node else 0

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y
