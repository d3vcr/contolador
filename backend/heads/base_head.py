 
class BaseHead:
    def __init__(self, start_channel: int, mode: str = "14CH"):
        self.start = start_channel - 1
        self.mode = mode.upper()

    def update_channel(self, data, offset, value):
        index = self.start + offset
        if 0 <= index < len(data):
            data[index] = value
