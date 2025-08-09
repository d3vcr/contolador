"""
Effects module for DMX moving heads.
Supports ColorChase, Strobe, and Rainbow effects.
"""

import threading
import time
import colorsys
import logging

class EffectManager:
    def __init__(self):
        self.current_effect = None
        self.running = False

    def run_effect(self, name, dmx_sender, start_address, heads, mode_channels):
        """Inicia el efecto seleccionado en un hilo separado."""
        self.stop_effect()  # Detiene cualquier efecto previo
        self.running = True
        self.current_effect = name
        thread = threading.Thread(
            target=self._dispatch_effect,
            args=(name, dmx_sender, start_address, heads, mode_channels),
            daemon=True
        )
        thread.start()

    def _dispatch_effect(self, name, dmx_sender, start_address, heads, mode_channels):
        """Llama a la función correspondiente del efecto."""
        if name == "ColorChase":
            self.color_chase(dmx_sender, start_address, heads, mode_channels)
        elif name == "Strobe":
            self.strobe(dmx_sender, start_address, heads, mode_channels)
        elif name == "Rainbow":
            self.rainbow(dmx_sender, start_address, heads, mode_channels)
        logging.info(f"Effect {name} finished")

    def stop_effect(self):
        """Detiene cualquier efecto en ejecución."""
        self.running = False
        self.current_effect = None

    def color_chase(self, dmx_sender, start_address, heads, mode_channels):
        """Cambia colores básicos en secuencia por cada cabeza."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        while self.running and self.current_effect == "ColorChase":
            for color in colors:
                for head in range(heads):
                    base = start_address - 1 + head * mode_channels
                    r_idx = base + (3 if mode_channels == 9 else 6)
                    dmx_sender.update_channel(r_idx, color[0])
                    dmx_sender.update_channel(r_idx + 1, color[1])
                    dmx_sender.update_channel(r_idx + 2, color[2])
                time.sleep(0.5)

    def strobe(self, dmx_sender, start_address, heads, mode_channels):
        """Enciende y apaga el canal de strobe a intervalos fijos."""
        on = False
        while self.running and self.current_effect == "Strobe":
            val = 255 if on else 0
            for head in range(heads):
                base = start_address - 1 + head * mode_channels
                idx = base + (2 if mode_channels == 9 else 5)
                dmx_sender.update_channel(idx, val)
            on = not on
            time.sleep(0.2)

    def rainbow(self, dmx_sender, start_address, heads, mode_channels):
        """Aplica un ciclo HSV de color arcoiris."""
        hue = 0.0
        while self.running and self.current_effect == "Rainbow":
            r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
            for head in range(heads):
                base = start_address - 1 + head * mode_channels
                r_idx = base + (3 if mode_channels == 9 else 6)
                dmx_sender.update_channel(r_idx, r)
                dmx_sender.update_channel(r_idx + 1, g)
                dmx_sender.update_channel(r_idx + 2, b)
            hue = (hue + 0.01) % 1.0
            time.sleep(0.1)

# Instancia única del manejador de efectos
effect_manager = EffectManager()

def run_effect(name, dmx_sender, start_address, heads, mode_channels):
    """Función externa para iniciar efectos."""
    effect_manager.run_effect(name, dmx_sender, start_address, heads, mode_channels)

def stop_effect():
    """Función externa para detener efectos."""
    effect_manager.stop_effect()
