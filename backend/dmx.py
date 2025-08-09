# === File: backend/dmx.py ===
"""
DMX communication module using MAX485 (Raspberry Pi UART / /dev/serial0).
- Robust error handling
- Safe start/stop of the send thread
- Bounds-checked channel updates
"""

import serial
import threading
import time
import logging


class DMXSender:
    """DMX sender for MAX485 connected to Raspberry Pi UART.

    Usage:
        d = DMXSender(port='/dev/serial0')
        d.start()                 # comienza a transmitir en hilo de fondo
        d.update_channel(0, 255)  # actualiza canal 1 (índice 0)
        d.stop()                  # detiene y cierra puerto
    """

    def __init__(self, port='/dev/serial0', baudrate=250000, num_channels=512, timeout=1.0):
        self.port = port
        self.baudrate = baudrate
        self.num_channels = int(num_channels)
        self.timeout = timeout

        self.lock = threading.Lock()
        self.dmx_data = bytearray([0] * self.num_channels)

        self._thread = None
        self.running = False

        try:
            self.serial = serial.Serial(
                port,
                baudrate=baudrate,
                stopbits=serial.STOPBITS_TWO,
                timeout=self.timeout,
            )
            logging.info(f"DMXSender: opened serial port {port} @ {baudrate}")
        except Exception as e:
            logging.exception(f"DMXSender: failed to open serial port {port}: {e}")
            # Rethrow so callers can handle (main app will show mensaje y salir limpio)
            raise

    def update_channel(self, addr, value):
        """Actualizar un canal DMX (addr: 0-based). Asegura 0..255 y dentro de rango."""
        with self.lock:
            if 0 <= addr < self.num_channels:
                self.dmx_data[addr] = int(max(0, min(255, int(value))))
            else:
                logging.warning(f"DMXSender.update_channel: addr {addr} fuera de rango")

    def _send_once(self):
        """Enviar un paquete DMX (break + MAB + datos)."""
        # Copiar datos bajo lock para minimizar tiempo bloqueado
        with self.lock:
            packet = bytearray([0]) + bytes(self.dmx_data)

        try:
            # DMX break — en Python sleep el mínimo práctico suele ser ~1ms; usamos 1ms para ser seguro
            self.serial.break_condition = True
            time.sleep(0.001)  # break (>= 88us en la especificación, 1ms es seguro)
            self.serial.break_condition = False
            time.sleep(0.001)  # MAB (mark after break)

            self.serial.write(packet)
            # Flush to reduce buffering delay
            try:
                self.serial.flush()
            except Exception:
                pass

        except Exception as e:
            logging.exception(f"DMXSender._send_once: error enviando paquete: {e}")

    def send_loop(self, interval=0.023):
        """Bucle de envío continuo. """
        logging.info("DMXSender: send loop started")
        next_time = time.time()
        while self.running:
            self._send_once()
            # control sencillo de frecuencia
            next_time += interval
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
        logging.info("DMXSender: send loop stopped")

    def start(self, interval=0.023):
        """Inicia el hilo de envío. Llamadas repetidas no reiniciarán múltiples hilos."""
        if self.running:
            logging.debug("DMXSender.start: ya estaba corriendo")
            return
        self.interval = float(interval)
        self.running = True
        self._thread = threading.Thread(target=self.send_loop, args=(self.interval,), daemon=True)
        self._thread.start()
        logging.info("DMXSender: started")

    def stop(self):
        """Detiene el hilo de envío y cierra el puerto serial de forma segura."""
        if not self.running:
            return
        self.running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        try:
            if hasattr(self, 'serial') and self.serial is not None and self.serial.is_open:
                self.serial.close()
                logging.info("DMXSender: serial port closed")
        except Exception:
            logging.exception("DMXSender.stop: error cerrando serial")

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass


# === End of backend/dmx.py ===
