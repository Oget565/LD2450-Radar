#ESP32MINI, mac = b'\x88V\xa6\\;\xf0'
from machine import UART, Pin
import time
import network
import espnow

uartradar1 = UART(1, baudrate=256000, tx=Pin(17), rx=Pin(18))
uartradar2 = UART(1, baudrate=256000, tx=Pin(4), rx=Pin(5))
uartlidar = UART(1, baudrate=256000, tx=Pin(6), rx=Pin(7)) 

sta = network.WLAN(network.WLAN.IF_STA)  
sta.active(True)

e = espnow.ESPNow()
e.active(True)
peer = b'\xf0\xf5\xbd\xfbgp'   # MAC address of peer's wifi interface, run print(sta.config('mac')) to find it
e.add_peer(peer)      

e.send(peer, "Starting...")
for i in range(100):
    e.send(peer, str(i)*20, True)
e.send(peer, b'end')

i = 0
fails = 0
e.send(peer, "Starting...")
while True:
    i += 1
    sent = e.send(peer, str(i))
    print(f"Sent {i}")
    host, msg = e.recv()
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
        