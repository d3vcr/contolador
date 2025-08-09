Conexiones de Hardware
=====================

Adaptador MAX485:
- Pin DI: Conectar a TX (/dev/ttyAMA0) de Raspberry Pi.
- Pin RO: Conectar a RX (/dev/ttyAMA0) de Raspberry Pi.
- VCC: Usar 3.3V (recomendado) o 5V (con precaución).
- GND: Conectar a GND de Raspberry Pi.

Sensores DHT11/DHT22:
- VCC: 3.3V o 5V (según sensor).
- Data: Conectar a un pin GPIO (ej. GPIO4).
- GND: Conectar a GND de Raspberry Pi.

LEDs Indicadores:
- Ánodo: Conectar a GPIO (ej. GPIO17) con resistencia.
- Cátodo: Conectar a GND.

Diagrama ASCII (MAX485 a Raspberry Pi):
Raspberry Pi       MAX485
GPIO14 (TX) ----> DI
GPIO15 (RX) <---- RO
3.3V -----------> VCC
GND -------------> GND