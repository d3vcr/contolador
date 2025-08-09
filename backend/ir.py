"""
IR module for handling IR emitter and receiver (phototransistor).
"""

import RPi.GPIO as GPIO
import time
import logging
import atexit

# Configuración de pines (modo BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # IR receiver
GPIO.setup(12, GPIO.OUT)  # IR emitter

def is_ir_detected():
    """Verifica si el sensor IR detecta un objeto (entrada baja)"""
    try:
        detected = GPIO.input(16) == 0
        logging.debug(f"IR detected: {detected}")
        return detected
    except Exception as e:
        logging.error(f"IR receiver error: {e}")
        return False

def send_ir_pulse():
    """Envía un pulso corto desde el emisor IR"""
    try:
        GPIO.output(12, 1)
        time.sleep(0.1)
        GPIO.output(12, 0)
        logging.info("IR pulse sent")
    except Exception as e:
        logging.error(f"IR emitter error: {e}")

def cleanup():
    """Libera los pines GPIO al cerrar el programa"""
    GPIO.cleanup()
    logging.info("GPIO cleanup executed")

# Registro automático para limpiar al salir del programa
atexit.register(cleanup)
