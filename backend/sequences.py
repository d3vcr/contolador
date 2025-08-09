import time
import json
import logging
from . import effects

class SequenceManager:
    def __init__(self):
        self.running = False
        self.current_sequence = None

    def run_sequence(self, dmx_sender, start_address, heads, mode_channels, sequence):
        """Ejecuta una secuencia de pasos con efectos o datos DMX."""
        self.running = True
        self.current_sequence = sequence
        try:
            for step in sequence:
                if not self.running:
                    break
                if "effect" in step:
                    effects.run_effect(step["effect"], dmx_sender, start_address, heads, mode_channels)
                    time.sleep(step.get("duration", 1))  # usa duración por defecto si no está
                    effects.stop_effect()
                elif "dmx" in step:
                    for addr_str, value in step["dmx"].items():
                        addr = int(addr_str) - 1
                        dmx_sender.update_channel(addr, value)
                    time.sleep(step.get("duration", 1))
                logging.info(f"Sequence step executed: {step}")
        except Exception as e:
            logging.error(f"Sequence error: {e}")
        finally:
            effects.stop_effect()  # Asegura que se detengan los efectos al finalizar

    def stop(self):
        """Detiene la ejecución de la secuencia."""
        self.running = False
        self.current_sequence = None

    def load_sequence(self, path):
        """Carga una secuencia desde un archivo JSON."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading sequence: {e}")
            return []

sequence_manager = SequenceManager()

def run_sequence(dmx_sender, start_address, heads, mode_channels, sequence):
    sequence_manager.run_sequence(dmx_sender, start_address, heads, mode_channels, sequence)

def stop_sequence():
    sequence_manager.stop()

def load_sequence(path):
    return sequence_manager.load_sequence(path)
