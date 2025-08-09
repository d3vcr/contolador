DMX Controller Ultimate

Descripción: DMX Controller Ultimate es una aplicación en Python basada en PyQt5 para controlar cabezas móviles y dispositivos DMX a través de un puerto serial. Diseñada para ser robusta y modular, permite controlar manualmente canales DMX, aplicar efectos dinámicos, guardar/cargar escenas, ejecutar secuencias, y monitorear sensores (DHT11/DHT22) e infrarrojos (IR). Ideal para iluminación en eventos, teatros o instalaciones interactivas, con soporte para Raspberry Pi, Windows y macOS.

Características:
- Control manual de canales DMX mediante sliders.
- Efectos dinámicos: ColorChase, Strobe, Rainbow, GoboPattern, AudioReactivity.
- Guardado/carga de escenas en archivos JSON.
- Ejecución de secuencias DMX predefinidas.
- Monitoreo en tiempo real de temperatura/humedad (DHT11/DHT22) y detección IR.
- Soporte para control remoto vía protocolo OSC.
- Interfaz gráfica con pestañas: Manual, Colores, Efectos, Escenas, Sensores, Secuencias.
- Manejo de errores con stubs para módulos faltantes y logging detallado.
- Compatible con Linux (Raspberry Pi), Windows y macOS.

Requisitos:
Software:
- Python 3.8 o superior
- PyQt5: `pip install PyQt5`
- Bibliotecas adicionales: `pip install -r requirements.txt`
- Sistema operativo: Linux (recomendado para Raspberry Pi), Windows, macOS
Hardware:
- Raspberry Pi (Pi 3 o 4 recomendado) u otro dispositivo con puerto serial.
- Adaptador DMX (ej. MAX485) conectado a /dev/ttyAMA0 o puerto equivalente.
- Cabezas móviles DMX configuradas en modo 9CH o 14CH.
- Sensores opcionales: DHT11/DHT22 (temperatura/humedad), sensor IR.
- LEDs opcionales para indicadores visuales.
- Micrófono opcional para reactividad de audio.

Instalación:
1. Clona el repositorio: `git clone https://github.com/d3vcr/contolador.git`
2. Entra al directorio: `cd CONTolador`
3. Crea un entorno virtual (opcional): `python3 -m venv venv` y actívalo: `source venv/bin/activate` (Linux/macOS) o `venv\Scripts\activate` (Windows)
4. Crea un archivo `requirements.txt` con: `PyQt5>=5.15.0` y ejecuta: `pip install -r requirements.txt`
5. Configura el puerto DMX: En Raspberry Pi, usa /dev/ttyAMA0. Asegura permisos: `sudo usermod -a -G dialout $USER`
6. Conecta hardware: Adaptador DMX (ej. MAX485) al puerto serial, cabezas móviles en modo 9CH/14CH, y sensores DHT11/DHT22 o IR (opcional).
7. Ejecuta: `python3 main.py`

Estructura del Proyecto:
- backend/__init__.py: Inicializa el paquete backend.
- backend/dmx.py: Gestiona la comunicación DMX vía serial.
- backend/effects.py: Define efectos dinámicos (ColorChase, Strobe, etc.).
- backend/sensors.py: Lee datos de sensores DHT11/DHT22.
- backend/scenes.py: Guarda/carga configuraciones DMX en JSON.
- backend/leds.py: Controla LEDs indicadores.
- backend/ir.py: Detecta señales infrarrojas.
- backend/audio.py: Procesa entrada de audio para efectos reactivos.
- backend/osc.py: Servidor OSC para control remoto.
- backend/sequences.py: Ejecuta secuencias DMX.
- logs/dmx_controller.log: Registro de logs.
- main.py: Interfaz gráfica (PyQt5) y lógica principal.
- requirements.txt: Dependencias.
- README.md: Este archivo.

Uso:
1. Ejecuta `python3 main.py` para abrir la interfaz.
2. Pestañas disponibles:
   - Manual: Ajusta sliders para canales DMX (modo 9CH/14CH, dirección inicial, número de cabezas).
   - Colors: Selecciona colores RGB.
   - Effects: Activa/detiene efectos (ajusta velocidad con slider).
   - Scenes: Guarda/carga configuraciones DMX.
   - View/Sensor: Monitorea temperatura/humedad.
   - Sequences: Ejecuta secuencias DMX.
3. Configuración DMX: Selecciona modo (9CH/14CH), dirección inicial (1-512), y número de cabezas (1-10). Usa "Blackout" para apagar todo.
4. Efectos/Secuencias: Inicia desde las pestañas Effects o Sequences. Los efectos se detienen al cambiar pestaña o con "Stop".
5. Sensores/IR: Monitoreo en View/Sensor; IR activa ColorChase.
6. Logs: Eventos en la interfaz y en logs/dmx_controller.log.

Notas de Hardware:
- Puerto serial (Raspberry Pi): Usa /dev/ttyAMA0. Deshabilita consola serial en /boot/config.txt: `sudo nano /boot/config.txt`, agrega `enable_uart=1` y `dtoverlay=disable-bt`, luego reinicia: `sudo reboot`.
- MAX485: Conecta DI a TX, RO a RX, GND común. Usa 3.3V (o 5V con cuidado).
- Cabezas móviles: Configura mismo modo y dirección inicial que en la app.

Solución de Problemas:
- Error de puerto serial: Verifica permisos (`sudo chmod 666 /dev/ttyAMA0`) o puerto en DMX_PORT.
- Módulos faltantes: Usa stubs; revisa advertencias en logs/dmx_controller.log.
- Sin movimiento: Confirma dirección, modo, conexiones DMX (prueba 3.3V).
- Errores GTK/ATK: Instala `sudo apt-get install libatk-adaptor libgail-common`.
- Errores de audio: Configura micrófono y bibliotecas (ej. pyaudio).
