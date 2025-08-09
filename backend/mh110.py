# backend/mh110.py

class MH110Head:
    def __init__(self, start_channel):
        self.start = start_channel - 1  # DMX channels are 1-indexed; Python uses 0-index

    def set_pan(self, data, value): data[self.start + 0] = value
    def set_pan_fine(self, data, value): data[self.start + 1] = value
    def set_tilt(self, data, value): data[self.start + 2] = value
    def set_tilt_fine(self, data, value): data[self.start + 3] = value
    def set_speed(self, data, value): data[self.start + 4] = value
    def set_dimmer(self, data, value): data[self.start + 5] = value

    def set_rgbw(self, data, r, g, b, w):
        data[self.start + 6] = r
        data[self.start + 7] = g
        data[self.start + 8] = b
        data[self.start + 9] = w

    def set_temp_color(self, data, value): data[self.start + 10] = value
    def set_internal_color(self, data, value): data[self.start + 11] = value
    def set_strobe(self, data, value): data[self.start + 12] = value
    def set_special_function(self, data, value): data[self.start + 13] = value
