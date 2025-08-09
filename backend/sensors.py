"""
Sensor module for reading DHT11/DHT22 temperature and humidity.
"""

import Adafruit_DHT
import logging

SENSOR_TYPES = {"DHT11": Adafruit_DHT.DHT11, "DHT22": Adafruit_DHT.DHT22}
DHT_PIN = 4

def read_dht(sensor_type):
    sensor = SENSOR_TYPES.get(sensor_type, Adafruit_DHT.DHT11)
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_PIN)
        if humidity is not None and temperature is not None:
            logging.info(f"Sensor read: Temp={temperature:.1f}°C, Hum={humidity:.1f}%")
            return humidity, temperature
        else:
            logging.warning("Failed to read sensor")
            return None, None
    except Exception as e:
        logging.error(f"Sensor error: {e}")
        return None, None
