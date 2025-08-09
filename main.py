# === File: main.py ===
"""
Main GUI application (PyQt5) para controlar cabezas móviles vía DMX.
Este archivo está corregido y reforzado:
- Manejo seguro del puerto DMX (usa backend.dmx.DMXSender)
- Inicialización robusta si faltan módulos secundarios (stubs)
- Hilos de sensores/IR seguras con Event para shutdown
- Actualización de la UI desde el hilo principal (QTimer)
- Limpieza ordenada al cerrar
"""

import os
import sys
import json
import time
import threading
import logging
import types
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox, QSpinBox, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer

# Crear carpeta de logs antes de configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/dmx_controller.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuración de puerto DMX (cámbiala aquí si usas otro puerto)
DMX_PORT = os.environ.get('DMX_PORT', '/dev/serial0')
DMX_BAUDRATE = int(os.environ.get('DMX_BAUDRATE', '250000'))

# Intentar importar módulos del /backend; si faltan, crear stubs que no rompan la app
try:
    from backend import dmx as dmx
except Exception as e:
    logging.exception('No se pudo importar backend.dmx; la aplicación no podrá usar DMX: %s', e)
    raise SystemExit(f"Error crítico: no se puede importar backend.dmx: {e}")

# Helper para stubs
def _stub_module(name):
    m = types.SimpleNamespace()
    def _noop(*a, **k):
        logging.warning(f"Stub {name} called with args={a} kwargs={k}")
    if name == 'effects':
        m.run_effect = lambda nm, dmx_obj, start_addr, heads, mode_ch: logging.warning('effects.run_effect (stub)')
        m.stop_effect = lambda : logging.warning('effects.stop_effect (stub)')
        class _EM:
            def set_speed(self, v): logging.warning('effects.effect_manager.set_speed (stub)')
        m.effect_manager = _EM()
    elif name == 'sensors':
        m.read_dht = lambda sensor_type: (None, None)
    elif name == 'scenes':
        def save_scene(data, path):
            try:
                with open(path, 'w') as f:
                    json.dump(list(data), f)
            except Exception:
                logging.exception('scenes.save_scene stub error')
        def load_scene(path):
            try:
                with open(path) as f:
                    arr = json.load(f)
                    return bytearray(arr)
            except Exception:
                logging.exception('scenes.load_scene stub error')
                return bytearray([0]*512)
        m.save_scene = save_scene
        m.load_scene = load_scene
    elif name == 'leds':
        m.set_led_color = lambda *a, **k: logging.info('leds.set_led_color (stub)')
        m.cleanup = lambda : logging.info('leds.cleanup (stub)')
    elif name == 'ir':
        m.is_ir_detected = lambda : False
    elif name == 'audio':
        m.run_audio_reactivity = lambda *a, **k: logging.warning('audio.run_audio_reactivity (stub)')
        m.stop_audio_reactivity = lambda : logging.warning('audio.stop_audio_reactivity (stub)')
    elif name == 'osc':
        m.start_osc_server = lambda *a, **k: logging.warning('osc.start_osc_server (stub)')
        m.stop_osc_server = lambda : logging.warning('osc.stop_osc_server (stub)')
    elif name == 'sequences':
        m.load_sequence = lambda p: None
        m.run_sequence = lambda *a, **k: logging.warning('sequences.run_sequence (stub)')
        m.stop_sequence = lambda : logging.warning('sequences.stop_sequence (stub)')
    return m

# Intentar importar los módulos no críticos y crear stubs si faltan
backend_names = ('effects', 'sensors', 'scenes', 'leds', 'ir', 'audio', 'osc', 'sequences')
backend = {}
for name in backend_names:
    try:
        mod = __import__(f'backend.{name}', fromlist=[name])
        backend[name] = mod
    except Exception:
        logging.warning(f"No se encontró backend.{name}. Se usa stub.")
        backend[name] = _stub_module(name)

effects = backend['effects']
sensors = backend['sensors']
scenes = backend['scenes']
leds = backend['leds']
ir = backend['ir']
audio = backend['audio']
osc = backend['osc']
sequences = backend['sequences']


class DMXControllerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMX Controller Ultimate")

        # Estado global
        self.start_address = 1
        self.mode_channels = 9
        self.heads = 2

        # Synchronization primitives
        self.shutdown_event = threading.Event()
        self.sensor_lock = threading.Lock()
        self.last_temperature = None
        self.last_humidity = None

        # DMX: inicializar y arrancar
        try:
            self.dmx = dmx.DMXSender(port=DMX_PORT, baudrate=DMX_BAUDRATE)
        except Exception as e:
            logging.exception('No se pudo inicializar DMXSender: %s', e)
            QMessageBox.critical(self, 'Error DMX', f'No se pudo abrir el puerto DMX ({DMX_PORT}).\n{e}')
            raise SystemExit(1)

        # Iniciar transmisión DMX en hilo propio del sender
        self.dmx.start()

        # UI
        self.init_ui()

        # Timers y hilos de soporte
        self.init_timers()
        self.start_threads()

        logging.info('Application initialized')

    # ------------------ UI ---------------------------------
    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.manual_tab(), "Manual")
        self.tabs.addTab(self.color_tab(), "Colors")
        self.tabs.addTab(self.effects_tab(), "Effects")
        self.tabs.addTab(self.scenes_tab(), "Scenes")
        self.tabs.addTab(self.view_tab(), "View/Sensor")
        self.tabs.addTab(self.sequences_tab(), "Sequences")
        layout.addWidget(self.tabs)

        # Log panel
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_view)

        self.setLayout(layout)
        self.log('UI initialized')

    def manual_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Configuration: mode, address, heads
        h_conf = QHBoxLayout()
        h_conf.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["9CH", "14CH"])
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        h_conf.addWidget(self.mode_combo)

        h_conf.addWidget(QLabel("Start Address:"))
        self.addr_spin = QSpinBox()
        self.addr_spin.setRange(1, 512)
        self.addr_spin.setValue(self.start_address)
        self.addr_spin.valueChanged.connect(self.change_address)
        h_conf.addWidget(self.addr_spin)

        h_conf.addWidget(QLabel("Heads:"))
        self.heads_spin = QSpinBox()
        self.heads_spin.setRange(1, 10)
        self.heads_spin.setValue(self.heads)
        self.heads_spin.valueChanged.connect(self.change_heads)
        h_conf.addWidget(self.heads_spin)
        layout.addLayout(h_conf)

        # Sliders for each head and channel
        self.sliders = {}
        self.slider_layout = QVBoxLayout()
        layout.addLayout(self.slider_layout)
        self.create_controls()

        # Buttons
        btn_blackout = QPushButton("Blackout")
        btn_blackout.clicked.connect(self.blackout)
        layout.addWidget(btn_blackout)

        tab.setLayout(layout)
        return tab

    def color_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        btn = QPushButton("Select Color")
        btn.clicked.connect(self.pick_color)
        layout.addWidget(btn)
        tab.setLayout(layout)
        return tab

    def effects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        for effect in ["ColorChase", "Strobe", "Rainbow", "GoboPattern", "AudioReactivity"]:
            btn = QPushButton(f"Start {effect}")
            btn.clicked.connect(lambda _, e=effect: self.run_effect(e))
            layout.addWidget(btn)
        btn_stop = QPushButton("Stop Effect")
        btn_stop.clicked.connect(self.stop_effect)
        layout.addWidget(btn_stop)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.update_effect_speed)
        layout.addWidget(QLabel("Effect Speed"))
        layout.addWidget(self.speed_slider)
        tab.setLayout(layout)
        return tab

    def scenes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        btn_save = QPushButton("Save Scene")
        btn_save.clicked.connect(self.save_scene)
        btn_load = QPushButton("Load Scene")
        btn_load.clicked.connect(self.load_scene)
        layout.addWidget(btn_save)
        layout.addWidget(btn_load)
        tab.setLayout(layout)
        return tab

    def view_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        h_s = QHBoxLayout()
        h_s.addWidget(QLabel("Sensor:"))
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItems(["DHT11", "DHT22"])
        h_s.addWidget(self.sensor_combo)
        layout.addLayout(h_s)
        self.sensor_label = QLabel("Temp: --°C  Hum: --%")
        layout.addWidget(self.sensor_label)
        tab.setLayout(layout)
        return tab

    def sequences_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        btn_load = QPushButton("Load Sequence")
        btn_load.clicked.connect(self.load_sequence)
        btn_run = QPushButton("Run Sequence")
        btn_run.clicked.connect(self.run_sequence)
        btn_stop = QPushButton("Stop Sequence")
        btn_stop.clicked.connect(self.stop_sequence)
        layout.addWidget(btn_load)
        layout.addWidget(btn_run)
        layout.addWidget(btn_stop)
        tab.setLayout(layout)
        return tab

    # ------------------ Helpers -----------------------------
    def clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)

    def create_controls(self):
        # Remove existing controls
        self.clear_layout(self.slider_layout)
        self.sliders = {}

        for head in range(self.heads):
            for ch in range(self.mode_channels):
                h_layout = QHBoxLayout()
                lbl = QLabel(f"H{head+1}-CH{ch+1}")
                slider = QSlider(Qt.Horizontal)
                slider.setRange(0, 255)
                # capture head and ch by default args
                slider.valueChanged.connect(lambda val, h=head, c=ch: self.update_dmx(h, c, val))
                h_layout.addWidget(lbl)
                h_layout.addWidget(slider)
                self.sliders[(head, ch)] = slider
                self.slider_layout.addLayout(h_layout)

        # After creating sliders, sync their positions from current DMX buffer
        self.sync_sliders_with_dmx()
        self.log(f"Controls created: {self.heads} heads x {self.mode_channels} channels")

    def sync_sliders_with_dmx(self):
        # Set each slider to reflect DMX buffer value (block signals to avoid feedback)
        for (head, ch), slider in self.sliders.items():
            addr = self.start_address - 1 + head * self.mode_channels + ch
            with self.dmx.lock:
                if 0 <= addr < len(self.dmx.dmx_data):
                    value = self.dmx.dmx_data[addr]
                else:
                    value = 0
            slider.blockSignals(True)
            slider.setValue(int(value))
            slider.blockSignals(False)

    # ------------------ Event handlers ---------------------
    def change_mode(self, index):
        self.mode_channels = 9 if index == 0 else 14
        self.create_controls()
        self.log(f"Changed to {self.mode_channels}CH mode")

    def change_address(self, value):
        self.start_address = int(value)
        # After address change, resync sliders to reflect new mapping
        self.sync_sliders_with_dmx()
        self.log(f"Start address set to d{str(value).zfill(3)}")

    def change_heads(self, value):
        self.heads = int(value)
        self.create_controls()
        self.log(f"Number of heads set to {self.heads}")

    def update_dmx(self, head, channel, value):
        addr = self.start_address - 1 + head * self.mode_channels + channel
        self.dmx.update_channel(addr, value)
        self.log(f"DMX channel {addr+1} set to {value}")

    def blackout(self):
        for head in range(self.heads):
            for ch in range(self.mode_channels):
                addr = self.start_address - 1 + head * self.mode_channels + ch
                self.dmx.update_channel(addr, 0)
        self.sync_sliders_with_dmx()
        self.log("Blackout activated")

    def pick_color(self):
        from PyQt5.QtGui import QColor
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            for head in range(self.heads):
                base = self.start_address - 1 + head * self.mode_channels
                # mapping RGB indices (heurística; depende de tu modo real)
                r_idx = base + (3 if self.mode_channels == 9 else 6)
                g_idx = r_idx + 1
                b_idx = r_idx + 2
                self.dmx.update_channel(r_idx, color.red())
                self.dmx.update_channel(g_idx, color.green())
                self.dmx.update_channel(b_idx, color.blue())
            self.sync_sliders_with_dmx()
            self.log(f"Color applied: {color.name()}")

    def save_scene(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Scene", filter="JSON Files (*.json)")
        if path:
            scenes.save_scene(self.dmx.dmx_data, path)
            self.log(f"Scene saved: {path}")

    def load_scene(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Scene", filter="JSON Files (*.json)")
        if path:
            data = scenes.load_scene(path)
            # data expected as iterable of ints
            for i, value in enumerate(data):
                self.dmx.update_channel(i, int(value))
            self.sync_sliders_with_dmx()
            self.log(f"Scene loaded: {path}")

    def run_effect(self, name):
        if getattr(self, 'effect_thread', None) and self.effect_thread.is_alive():
            self.log("Another effect is running")
            return
        if name == "AudioReactivity":
            self.effect_thread = threading.Thread(
                target=lambda: audio.run_audio_reactivity(self.dmx, self.start_address, self.heads, self.mode_channels),
                daemon=True
            )
        else:
            self.effect_thread = threading.Thread(
                target=lambda: effects.run_effect(name, self.dmx, self.start_address, self.heads, self.mode_channels),
                daemon=True
            )
        self.effect_thread.start()
        self.log(f"Effect {name} started")
        leds.set_led_color(0, 0, 1)

    def stop_effect(self):
        try:
            effects.stop_effect()
            audio.stop_audio_reactivity()
        except Exception:
            logging.exception('Error stopping effect/audio')
        self.effect_thread = None
        self.log("Effect stopped")
        leds.set_led_color(0, 1, 0)

    def update_effect_speed(self, value):
        try:
            effects.effect_manager.set_speed(value)
            self.log(f"Effect speed set to {value}%")
        except Exception:
            logging.exception('Error setting effect speed')

    def load_sequence(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Sequence", filter="JSON Files (*.json)")
        if path:
            self.current_sequence = sequences.load_sequence(path)
            self.log(f"Sequence loaded: {path}")

    def run_sequence(self):
        if hasattr(self, 'current_sequence') and self.current_sequence:
            if getattr(self, 'sequence_thread', None) and self.sequence_thread.is_alive():
                self.log("Another sequence is running")
                return
            self.sequence_thread = threading.Thread(
                target=lambda: sequences.run_sequence(self.dmx, self.start_address, self.heads, self.mode_channels, self.current_sequence),
                daemon=True
            )
            self.sequence_thread.start()
            self.log("Sequence started")
            leds.set_led_color(0, 0, 1)
        else:
            self.log("No sequence loaded")

    def stop_sequence(self):
        try:
            sequences.stop_sequence()
        except Exception:
            logging.exception('Error stopping sequence')
        self.sequence_thread = None
        self.log("Sequence stopped")
        leds.set_led_color(0, 1, 0)

    # ------------------ Background threads -----------------
    def init_timers(self):
        # Timer to update UI from data produced by background threads
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(1000)

    def start_threads(self):
        # Sensor reader thread: escribe última lectura en variables protegidas
        self.sensor_thread = threading.Thread(target=self.read_sensors, daemon=True)
        self.sensor_thread.start()

        # IR monitor thread
        self.ir_thread = threading.Thread(target=self.monitor_ir, daemon=True)
        self.ir_thread.start()

        # OSC server thread (delegado al módulo)
        try:
            self.osc_thread = threading.Thread(target=lambda: osc.start_osc_server(self.dmx), daemon=True)
            self.osc_thread.start()
        except Exception:
            logging.exception('No se pudo iniciar osc server')

        logging.info('Threads started: Sensor, IR, OSC')

    def read_sensors(self):
        while not self.shutdown_event.is_set():
            try:
                humidity, temperature = sensors.read_dht(self.sensor_combo.currentText())
                with self.sensor_lock:
                    self.last_humidity = humidity
                    self.last_temperature = temperature
            except Exception:
                logging.exception('Error leyendo sensores')
            # frecuencia de lectura
            self.shutdown_event.wait(1.0)

    def monitor_ir(self):
        while not self.shutdown_event.is_set():
            try:
                if ir.is_ir_detected():
                    # Ejecutar un efecto inmediato (se hace en thread nuevo dentro de run_effect)
                    self.run_effect("ColorChase")
                    leds.set_led_color(0, 0, 1)
                else:
                    leds.set_led_color(0, 1, 0)
            except Exception:
                logging.exception('Error en monitor_ir')
            self.shutdown_event.wait(0.1)

    def update_sensor(self):
        # Actualizar la UI desde las últimas lecturas de sensor (manejado en hilo principal)
        with self.sensor_lock:
            h = self.last_humidity
            t = self.last_temperature
        if h is not None and t is not None:
            self.sensor_label.setText(f"Temp: {t:.1f}°C  Hum: {h:.1f}%")

    # ------------------ Logging / cierre -------------------
    def log(self, msg):
        ts = time.strftime('%H:%M:%S')
        try:
            self.log_view.append(f"{ts} - {msg}")
        except Exception:
            logging.exception('Error appending to log_view')
        logging.info(msg)

    def closeEvent(self, event):
        logging.info('Shutting down application...')
        # Señalizar a los hilos que paren
        self.shutdown_event.set()

        # Detener efectos/sequence/OSC
        try:
            effects.stop_effect()
        except Exception:
            pass
        try:
            audio.stop_audio_reactivity()
        except Exception:
            pass
        try:
            sequences.stop_sequence()
        except Exception:
            pass
        try:
            osc.stop_osc_server()
        except Exception:
            pass

        # Parar DMX y limpiar LEDs
        try:
            self.dmx.stop()
        except Exception:
            logging.exception('Error deteniendo DMX')
        try:
            leds.cleanup()
        except Exception:
            logging.exception('Error limpiando LEDs')

        logging.info('Shutdown complete')
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = DMXControllerApp()
    controller.resize(1000, 700)
    controller.show()
    sys.exit(app.exec_())

# === End of main.py ===
