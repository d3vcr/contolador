"""
LED control module for RGB indicators.
"""

import RPi.GPIO as GPIO
import logging

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)   # Red LED
GPIO.setup(6, GPIO.OUT)   # Green LED
GPIO.setup(13, GPIO.OUT)  # Blue LED

def set_led_color(red, green, blue):
    try:
        GPIO.output(5, GPIO.HIGH if red else GPIO.LOW)
        GPIO.output(6, GPIO.HIGH if green else GPIO.LOW)
        GPIO.output(13, GPIO.HIGH if blue else GPIO.LOW)
        logging.info(f"LEDs set: R={red}, G={green}, B={blue}")
    except Exception as e:
        logging.error(f"LED error: {e}")

def cleanup():
    GPIO.cleanup()
    logging.info("GPIO cleaned up")

# Initialize LEDs off
set_led_color(0, 0, 0)
