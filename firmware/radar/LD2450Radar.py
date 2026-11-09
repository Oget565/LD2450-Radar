#ESP32MINI, mac = b'\x88V\xa6\\;\xf0'
from machine import UART, Pin, ADC
import time
import network
import espnow
import struct
import json

class ReadRadar:
    HEADER = b'\xaa\xff\x03\x00'
    TAIL = b'\x55\xcc'

    def __init__(self, uart):
        self.uart = uart
        self.buf = b''
        self.targets = []

    def decode(self, raw):
        if raw & 0x8000:
            return raw - 0x8000
        return -raw

    def read(self):
        data = self.uart.read()
        if data:
            self.buf += data
        frame = None
        while True:
            i = self.buf.find(self.HEADER)
            if i < 0:
                self.buf = self.buf[-3:]
                break
            if len(self.buf) < i + 30:
                self.buf = self.buf[i:]
                break
            f = self.buf[i:i + 30]
            self.buf = self.buf[i + 30:]
            if f[28:30] == self.TAIL:
                frame = f
        if frame is not None:
            targets = []
            for n in range(3):
                x, y, speed, res = struct.unpack('<HHHH', frame[4 + n * 8:12 + n * 8])
                if x == 0 and y == 0 and speed == 0 and res == 0:
                    continue
                targets.append((self.decode(x), self.decode(y), self.decode(speed), res))
            self.targets = targets
        return self.targets

class ReadLidar:
    HEADER = b'\x59\x59'

    def __init__(self, uart):
        self.uart = uart
        self.buf = b''
        self.distance = None
        self.strength = None
        self.temp = None

    def read(self):
        data = self.uart.read()
        if data:
            self.buf += data
        frame = None
        while True:
            i = self.buf.find(self.HEADER)
            if i < 0:
                self.buf = self.buf[-1:]
                break
            if len(self.buf) < i + 9:
                self.buf = self.buf[i:]
                break
            f = self.buf[i:i + 9]
            if sum(f[:8]) & 0xFF == f[8]:
                frame = f
                self.buf = self.buf[i + 9:]
            else:
                self.buf = self.buf[i + 1:]
        if frame is not None:
            dist, strength, temp = struct.unpack('<HHH', frame[2:8])
            self.distance = dist
            self.strength = strength
            self.temp = temp / 8 - 256
        return self.distance

uartradar1 = UART(1, baudrate=256000, tx=Pin(17), rx=Pin(18), rxbuf=1024)
uartradar2 = UART(2, baudrate=256000, tx=Pin(4), rx=Pin(5), rxbuf=1024)
uartlidar = UART(0, baudrate=115200, tx=Pin(6), rx=Pin(7), rxbuf=512)

radar1 = ReadRadar(uartradar1)
radar2 = ReadRadar(uartradar2)
lidar = ReadLidar(uartlidar)

VBattADC = ADC(Pin(2))
VBattADC.atten(ADC.ATTN_11DB)
Vbatt = 2 * ((VBattADC.read_u16() / 65535) * 3.3)

sta = network.WLAN(network.WLAN.IF_STA)  
sta.active(True)

e = espnow.ESPNow()
e.active(True)
peer = b'\xf0\xf5\xbd\xfbgp'   # MAC address of peer's wifi interface, run print(sta.config('mac')) to find it
e.add_peer(peer)      

fails = 0
e.send(peer, "Starting...")
while True:
    Vbatt = 2 * ((VBattADC.read_u16() / 65535) * 3.3)
    data = {
        "i": i,
        "r1": radar1.read(),
        "r2": radar2.read(),
        "l": lidar.read(),
        "b": round(Vbatt, 2)
    }
    
    sent = e.send(peer, json.dumps(data))
    print(f"Sent {data}")
    host, msg = e.recv(200)
    if sent and msg:
        fails = 0
        if host == peer:
            print(f"Recieved {msg} from ESP32")
        else:
            print(host, msg)
    else:
        fails += 1
        
    if fails >= 5:
        print ("ESP32 Is not responding")
        break
        