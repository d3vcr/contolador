 
"""
StageWashHead: Clase para controlar el modelo Monoprice Stage Wash 7x10W RGBW (P/N 612870).
Soporta modos de 9 y 14 canales DMX.
"""

class StageWashHead:
    def __init__(self, start_channel: int, mode: str = "14CH"):
        self.start = start_channel - 1  # 0-based index
        self.mode = mode.upper()

    def set_pan(self, data, value):
        data[self.start + 0] = value

    def set_tilt(self, data, value):
        data[self.start + (2 if self.mode == "14CH" else 1)] = value

    def set_pan_fine(self, data, value):
        if self.mode == "14CH":
            data[self.start + 1] = value

    def set_tilt_fine(self, data, value):
        if self.mode == "14CH":
            data[self.start + 3] = value

    def set_speed(self, data, value):
        idx = 4 if self.mode == "14CH" else 7
        data[self.start + idx] = value

    def set_dimmer(self, data, value):
        idx = 5 if self.mode == "14CH" else 2
        data[self.start + idx] = value

    def set_rgbw(self, data, r, g, b, w):
        if self.mode == "14CH":
            data[self.start + 6] = r
            data[self.start + 7] = g
            data[self.start + 8] = b
            data[self.start + 9] = w
        else:
            data[self.start + 3] = r
            data[self.start + 4] = g
            data[self.start + 5] = b
            data[self.start + 6] = w

    def set_macro_mix(self, data, value):
        if self.mode == "14CH":
            data[self.start + 10] = value  # RGBW Color Mixing and Random

    def set_mix_speed(self, data, value):
        if self.mode == "14CH":
            data[self.start + 11] = value  # Color Mixing Speed

    def set_function_mode(self, data, value):
        if self.mode == "14CH":
            data[self.start + 12] = value  # Auto/Sound Activated

    def reset(self, data):
        idx = 13 if self.mode == "14CH" else 8
        data[self.start + idx] = 255  # Reset (any value 1–255 activa reset momentáneo)
