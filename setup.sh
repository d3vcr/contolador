#!/bin/bash
echo "Configurando DMX Controller Ultimate..."
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
# Instalar dependencias
pip install -r requirements.txt
# Configurar permisos para puerto serial
sudo usermod -a -G dialout $USER
# Deshabilitar consola serial en Raspberry Pi
sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
echo "Configuración completada. Reinicia la Raspberry Pi y ejecuta 'python3 main.py'."