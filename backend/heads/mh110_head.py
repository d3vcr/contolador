from .base_head import BaseHead

class MH110Head(BaseHead):
    def set_pan(self, data, value): self.update_channel(data, 0, value)
    def set_pan_fine(self, data, value): self.update_channel(data, 1, value)
    def set_tilt(self, data, value): self.update_channel(data, 2, value)
    def set_tilt_fine(self, data, value): self.update_channel(data, 3, value)
    def set_speed(self, data, value): self.update_channel(data, 4, value)
    def set_dimmer(self, data, value): self.update_channel(data, 5, value)

    def set_rgbw(self, data, r, g, b, w):
        self.update_channel(data, 6, r)
        self.update_channel(data, 7, g)
        self.update_channel(data, 8, b)
        self.update_channel(data, 9, w)

    def set_temp_color(self, data, value): self.update_channel(data, 10, value)
    def set_internal_color(self, data, value): self.update_channel(data, 11, value)
    def set_strobe(self, data, value): self.update_channel(data, 12, value)
    def set_special_function(self, data, value): self.update_channel(data, 13, value)
