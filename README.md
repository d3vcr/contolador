#DMX Controller Ultimate
#DMX Controller Ultimate es una aplicación Python basada en PyQt5 para controlar cabezas móviles y dispositivos DMX a través de un puerto serial. Diseñada para ser robusta y modular, permite controlar manualmente canales DMX, aplicar efectos, guardar/cargar escenas, ejecutar secuencias, y monitorear sensores (DHT11/DHT22) e infrarrojos (IR). La aplicación es ideal para aplicaciones de iluminación en eventos, teatros, o instalaciones interactivas, con soporte para Raspberry Pi y otras plataformas.
#Características
	•	Control Manual: Ajuste de canales DMX mediante sliders para cada cabeza y canal.
	•	Efectos Dinámicos: Incluye efectos como ColorChase, Strobe, Rainbow, GoboPattern, y AudioReactivity.
	•	Escenas: Guarda y carga configuraciones DMX en archivos JSON.
	•	Secuencias: Ejecuta secuencias predefinidas de comandos DMX.
	•	Sensores: Monitorea temperatura y humedad (DHT11/DHT22) en tiempo real.
	•	Detección IR: Activa efectos automáticos al detectar señales infrarrojas.
	•	OSC: Soporte para control remoto vía protocolo OSC.
	•	Interfaz Gráfica: Interfaz intuitiva con pestañas para manual, colores, efectos, escenas, sensores, y secuencias.
	•	Robustez: Manejo de errores con stubs para módulos faltantes y logging detallado.
	•	Multiplataforma: Compatible con Linux (Raspberry Pi), Windows, y macOS.
Requisitos
Software
	•	Python: 3.8 o superior
	•	PyQt5: pip install PyQt5
	•	Bibliotecas adicionales: pip install -r requirements.txt (ver abajo)
	•	Sistema operativo: Linux (recomendado para Raspberry Pi), Windows, o macOS
Hardware
	•	Raspberry Pi (recomendado: Pi 3 o 4) u otro dispositivo con puerto serial.
	•	Adaptador DMX: Conexión serial (por ejemplo, MAX485) conectado a /dev/ttyAMA0 o puerto equivalente.
	•	Cabezas móviles DMX: Configuradas en modo 9CH o 14CH.
	•	Sensores (opcional): DHT11/DHT22 para temperatura/humedad, sensor IR para detección.
	•	LEDs (opcional): Para indicadores visuales (integración con módulo leds).
	•	Micrófono (opcional): Para reactividad de audio (módulo audio).
Instalación
	1	Clonar el repositorio: git clone https://github.com//dmx-controller-ultimate.git
	2	cd dmx-controller-ultimate
	3	
	4	Crear entorno virtual (opcional, recomendado): python3 -m venv venv
	5	source venv/bin/activate  # Linux/macOS
	6	venv\Scripts\activate     # Windows
	7	
	8	Instalar dependencias: Crea un archivo requirements.txt con: PyQt5>=5.15.0
	9	 Luego ejecuta: pip install -r requirements.txt
	10	
	11	Configurar puerto DMX:
	◦	En Raspberry Pi, usa /dev/ttyAMA0 para el puerto serial (o verifica tu adaptador DMX).
	◦	Asegúrate de que el usuario tiene permisos para el puerto: sudo usermod -a -G dialout $USER
	◦	
	12	Conectar hardware:
	◦	Conecta el adaptador DMX al puerto serial (por ejemplo, MAX485 a /dev/ttyAMA0).
	◦	Configura las cabezas móviles en modo 9CH o 14CH y asigna direcciones iniciales.
	◦	(Opcional) Conecta sensores DHT11/DHT22 y IR según el módulo sensors e ir.
	13	Ejecutar la aplicación: python3 main.py
	14	
Estructura del Proyecto
dmx-controller-ultimate/
├── backend/
│   ├── __init__.py         # Inicialización del paquete backend
│   ├── dmx.py              # Gestión de comunicación DMX (serial)
│   ├── effects.py          # Efectos dinámicos (ColorChase, Strobe, etc.)
│   ├── sensors.py          # Lectura de sensores DHT11/DHT22
│   ├── scenes.py           # Guardado/carga de escenas DMX
│   ├── leds.py             # Control de LEDs indicadores
│   ├── ir.py               # Detección de señales infrarrojas
│   ├── audio.py            # Reactividad de audio
│   ├── osc.py              # Servidor OSC para control remoto
│   ├── sequences.py        # Ejecución de secuencias DMX
├── logs/
│   ├── dmx_controller.log  # Registro de logs de la aplicación
├── main.py                 # Aplicación principal (GUI con PyQt5)
├── requirements.txt        # Dependencias de Python
├── README.md               # Este archivo
Descripción de Archivos
	•	main.py: Punto de entrada de la aplicación. Implementa la interfaz gráfica (PyQt5) con pestañas para control manual, colores, efectos, escenas, sensores, y secuencias. Gestiona hilos para tareas en segundo plano y sincroniza sliders con el buffer DMX.
	•	backend/dmx.py: Maneja la comunicación DMX a través del puerto serial. Incluye clase DMXSender para enviar datos a cabezas móviles.
	•	backend/effects.py: Define efectos dinámicos como ColorChase, Strobe, Rainbow, GoboPattern, y AudioReactivity.
	•	backend/sensors.py: Lee datos de sensores DHT11/DHT22 para temperatura y humedad.
	•	backend/scenes.py: Permite guardar y cargar configuraciones DMX en archivos JSON.
	•	backend/leds.py: Controla LEDs indicadores (por ejemplo, azul para efectos activos, verde para inactivos).
	•	backend/ir.py: Detecta señales infrarrojas para activar efectos automáticamente.
	•	backend/audio.py: Procesa entrada de audio para efectos reactivos.
	•	backend/osc.py: Implementa un servidor OSC para control remoto.
	•	backend/sequences.py: Ejecuta secuencias predefinidas de comandos DMX.
	•	logs/dmx_controller.log: Archivo de logs generado automáticamente para depuración.
Uso
	1	Lanzar la aplicación: Ejecuta python3 main.py. La interfaz se abrirá con varias pestañas.
	2	Pestañas disponibles:
	◦	Manual: Ajusta sliders para controlar canales DMX por cabeza. Configura modo (9CH/14CH), dirección inicial, y número de cabezas.
	◦	Colors: Selecciona colores RGB para aplicar a las cabezas.
	◦	Effects: Inicia/detiene efectos como ColorChase o AudioReactivity. Ajusta velocidad con un slider.
	◦	Scenes: Guarda o carga configuraciones DMX en archivos JSON.
	◦	View/Sensor: Muestra lecturas de temperatura y humedad (DHT11/DHT22).
	◦	Sequences: Carga y ejecuta secuencias DMX desde archivos JSON.
	3	Configuración DMX:
	◦	Selecciona el modo (9CH o 14CH) en la pestaña Manual.
	◦	Ajusta la dirección inicial (1-512) y el número de cabezas (1-10).
	◦	Usa el botón “Blackout” para apagar todas las cabezas.
	4	Efectos y Secuencias:
	◦	Inicia efectos desde la pestaña Effects o secuencias desde Sequences.
	◦	Los efectos se detienen automáticamente al cambiar de pestaña o con el botón “Stop”.
	5	Sensores e IR:
	◦	Monitorea temperatura/humedad en la pestaña View/Sensor.
	◦	La detección IR activa automáticamente el efecto ColorChase.
	6	Logs:
	◦	Los eventos se registran en la interfaz y en logs/dmx_controller.log.
Notas de Hardware
	•	Puerto Serial: En Raspberry Pi, usa /dev/ttyAMA0 (UART principal). Asegúrate de deshabilitar la consola serial en /boot/config.txt: sudo nano /boot/config.txt
	•	# Agrega o verifica:
	•	enable_uart=1
	•	dtoverlay=disable-bt
	•	 Luego reinicia: sudo reboot.
	•	MAX485: Conecta el adaptador DMX al puerto serial con VCC a 3.3V (recomendado) o 5V (prueba con cuidado). Verifica las conexiones:
	◦	Pin DI (MAX485) al TX del puerto serial.
	◦	Pin RO (MAX485) al RX del puerto serial.
	◦	GND común entre Raspberry Pi y MAX485.
	•	Cabezas móviles: Configura las cabezas en el mismo modo (9CH/14CH) y dirección inicial que en la aplicación.
Solución de Problemas
	•	Error de puerto serial: Verifica permisos (sudo chmod 666 /dev/ttyAMA0) o usa otro puerto en la variable de entorno DMX_PORT.
	•	Módulos backend faltantes: La aplicación usa stubs para módulos no encontrados, pero registra advertencias en el log.
	•	Sin movimiento en cabezas: Confirma la dirección inicial, modo, y conexiones del adaptador DMX. Prueba con 3.3V en lugar de 5V.
	•	Errores GTK/ATK: Instala paquetes de accesibilidad: sudo apt-get install libatk-adaptor libgail-common
	•	
	•	Errores de audio: Asegúrate de tener un micrófono configurado y las bibliotecas necesarias (por ejemplo, pyaudio).
Contribuir
	1	Crea un fork del repositorio.
	2	Crea una rama para tu funcionalidad: git checkout -b feature/nueva-funcionalidad.
	3	Envía un pull request con una descripción clara de los cambios.
, 