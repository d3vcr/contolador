"""
OSC server module for remote DMX control.
"""

from pythonosc import osc_server, dispatcher
import threading
import logging

class OSCServer:
    def __init__(self, ip="0.0.0.0", port=9000):
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/dmx/channel", self.handle_dmx)
        self.dmx_sender = None
        self.running = False
        self.server = osc_server.ThreadingOSCUDPServer((ip, port), self.dispatcher)
        logging.info(f"OSC server initialized on {ip}:{port}")

    def handle_dmx(self, address, channel, value):
        if self.dmx_sender:
            self.dmx_sender.update_channel(channel - 1, int(value))
            logging.info(f"OSC: Set channel {channel} to {value}")

    def start(self, dmx_sender):
        self.dmx_sender = dmx_sender
        self.running = True
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def stop(self):
        self.running = False
        self.server.shutdown()

osc_server = OSCServer()

def start_osc_server(dmx_sender):
    osc_server.start(dmx_sender)

def stop_osc_server():
    osc_server.stop()
