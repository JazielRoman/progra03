class HashNode:
    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next = next_node

class HashMap:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        self.size = 0
        self.buckets = [None] * capacity

    def _hash(self, key) -> int:
        return (hash(key) & 0x7FFFFFFF) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        head = self.buckets[idx]
        current = head
        while current:
            if current.key == key:
                current.value = value
                return
            current = current.next
        new_node = HashNode(key, value, head)
        self.buckets[idx] = new_node
        self.size += 1

    def get(self, key):
        idx = self._hash(key)
        current = self.buckets[idx]
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def exists(self, key) -> bool:
        return self.get(key) is not None

    def keys(self):
        all_keys = []
        for head in self.buckets:
            current = head
            while current:
                all_keys.append(current.key)
                current = current.next
        return all_keys

    def __len__(self):
        return self.size
