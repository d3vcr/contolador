import sys
import time
import threading
import logging

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QTabWidget, QPushButton, QTextEdit, QComboBox,
    QSpinBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer

import dmx
import scenes
import effects
import leds
import sensors
import ir

# Configuración de logging
logging.basicConfig(
    filename='logs/dmx_controller.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DMXControllerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMX Controller Ultimate")

        self.dmx_sender = dmx.DMXSender()
        self.dmx_sender.start()

        self.init_ui()
        self.setup_timers()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.manual_tab = QWidget()
        self.effects_tab = QWidget()
        self.scenes_tab = QWidget()
        self.sensors_tab = QWidget()
        self.ir_tab = QWidget()

        self.tabs.addTab(self.manual_tab, "Control Manual")
        self.tabs.addTab(self.effects_tab, "Efectos")
        self.tabs.addTab(self.scenes_tab, "Escenas")
        self.tabs.addTab(self.sensors_tab, "Sensores")
        self.tabs.addTab(self.ir_tab, "Control IR")

        self.layout.addWidget(self.tabs)

        self.init_manual_tab()
        # Aquí podrías inicializar las otras pestañas también (effects, scenes...)

    def init_manual_tab(self):
        layout = QVBoxLayout()
        self.sliders = []

        for channel in range(16):
            hbox = QHBoxLayout()
            label = QLabel(f"Canal {channel+1}")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(255)
            slider.setValue(0)
            slider.valueChanged.connect(lambda val, ch=channel: self.dmx_sender.update_channel(ch, val))
            hbox.addWidget(label)
            hbox.addWidget(slider)
            layout.addLayout(hbox)
            self.sliders.append(slider)

        self.manual_tab.setLayout(layout)

    def setup_timers(self):
        # Aquí puedes agregar timers si los necesitas
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)  # Cada 1 segundo

    def update_ui(self):
        # Ejemplo: lectura de sensor o feedback visual
        pass

    def closeEvent(self, event):
        self.dmx_sender.stop()
        logging.info("Cerrando aplicación DMX Controller.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DMXControllerApp()
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec_())
