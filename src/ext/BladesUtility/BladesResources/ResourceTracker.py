

class ResourceTracker:
    def __init__(self, value: int, max_resource: int):
        self.value: int = value
        self.max_resource: int = max_resource

    def set_value(self, value: int):
        self.value = max(0, min(self.max_resource, value))

    def set_max_value(self, max_stress: int):
        self.max_resource = max(max_stress, 0)
        self.value = max(0, min(self.max_resource, self.value))

