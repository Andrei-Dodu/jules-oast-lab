class LRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}

    def get(self, key):
        if key not in self.data:
            return None
        val = self.data.pop(key)
        self.data[key] = val
        return val

    def put(self, key, value):
        if key in self.data:
            self.data.pop(key)
        elif len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        self.data[key] = value
