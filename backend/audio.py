"""
Audio reactivity module for DMX Controller.
Maps audio input to DMX values for moving heads.
"""

import pyaudio
import numpy as np
import threading
import logging

class AudioReactivity:
    def __init__(self):
        self.running = False
        self.lock = threading.Lock()

    def audio_reactivity(self, dmx_sender, start_address, heads, mode_channels):
        CHUNK = 1024
        RATE = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

        try:
            while self.running:
                data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
                level = np.abs(data).mean() / 32768 * 255  # Normalize to 0-255
                for head in range(heads):
                    base = start_address - 1 + head * mode_channels
                    r_idx = base + (3 if mode_channels == 9 else 6)
                    g_idx = r_idx + 1
                    b_idx = r_idx + 2
                    dimmer_idx = base + (2 if mode_channels == 9 else 5)
                    dmx_sender.update_channel(r_idx, int(level))
                    dmx_sender.update_channel(g_idx, int(255 - level))
                    dmx_sender.update_channel(b_idx, int(level / 2))
                    dmx_sender.update_channel(dimmer_idx, int(level))
                logging.debug(f"Audio level: {level:.1f}")
        except Exception as e:
            logging.error(f"Audio error: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            logging.info("Audio reactivity stopped")

    def start(self, dmx_sender, start_address, heads, mode_channels):
        with self.lock:
            if self.running:
                logging.warning("Audio reactivity already running")
                return
            self.running = True
            threading.Thread(
                target=self.audio_reactivity,
                args=(dmx_sender, start_address, heads, mode_channels),
                daemon=True
            ).start()

    def stop(self):
        with self.lock:
            self.running = False

audio_reactivity = AudioReactivity()

def run_audio_reactivity(dmx_sender, start_address, heads, mode_channels):
    audio_reactivity.start(dmx_sender, start_address, heads, mode_channels)

def stop_audio_reactivity():
    audio_reactivity.stop()
