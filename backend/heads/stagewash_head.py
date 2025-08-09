 
from .base_head import BaseHead

class StageWashHead(BaseHead):
    def set_pan(self, data, value): self.update_channel(data, 0, value)

    def set_tilt(self, data, value):
        self.update_channel(data, 2 if self.mode == "14CH" else 1, value)

    def set_pan_fine(self, data, value):
        if self.mode == "14CH":
            self.update_channel(data, 1, value)

    def set_tilt_fine(self, data, value):
        if self.mode == "14CH":
            self.update_channel(data, 3, value)

    def set_speed(self, data, value):
        self.update_channel(data, 4 if self.mode == "14CH" else 7, value)

    def set_dimmer(self, data, value):
        self.update_channel(data, 5 if self.mode == "14CH" else 2, value)

    def set_rgbw(self, data, r, g, b, w):
        if self.mode == "14CH":
            base = 6
        else:
            base = 3
        self.update_channel(data, base + 0, r)
        self.update_channel(data, base + 1, g)
        self.update_channel(data, base + 2, b)
        self.update_channel(data, base + 3, w)

    def set_macro_mix(self, data, value):
        if self.mode == "14CH":
            self.update_channel(data, 10, value)

    def set_mix_speed(self, data, value):
        if self.mode == "14CH":
            self.update_channel(data, 11, value)

    def set_function_mode(self, data, value):
        if self.mode == "14CH":
            self.update_channel(data, 12, value)

    def reset(self, data):
        self.update_channel(data, 13 if self.mode == "14CH" else 8, 255)
