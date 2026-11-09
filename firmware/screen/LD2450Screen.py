#ESP32OLED, mac = b'\xf0\xf5\xbd\xfbgp'
from machine import Pin, ADC, SPI
import network
import espnow
import json
import math
from ili9341 import Display, color565

class RadarScreen:
    WIDTH = 320
    HEIGHT = 240
    OX = 160
    OY = 172
    R = 140
    MAX_RANGE = 6000
    HALF_FOV = 112
    RADAR_OFFSET = 52
    FLIP_X = False
    RINGS = (2000, 4000, 6000)
    DOT = 4

    BLACK = color565(0, 0, 0)
    SECTOR = color565(0, 24, 8)
    GRID = color565(0, 110, 40)
    TEXT = color565(220, 220, 220)
    RADAR1 = color565(0, 200, 255)
    RADAR2 = color565(255, 140, 0)
    LIDAR = color565(255, 0, 80)
    WARN = color565(255, 40, 40)
    OK = color565(0, 220, 0)

    def __init__(self, display):
        self.display = display
        self.scale = self.R / self.MAX_RANGE
        self.ring_px = [r * self.scale for r in self.RINGS]
        self.edge = math.radians(self.HALF_FOV)
        self.dots = []
        self.draw_background()

    def draw_background(self):
        d = self.display
        d.clear(self.BLACK)
        cut = math.tan(math.radians(180 - self.HALF_FOV))
        for y in range(self.OY - self.R, self.HEIGHT):
            dy = self.OY - y
            if abs(dy) > self.R:
                continue
            half = int(math.sqrt(self.R * self.R - dy * dy))
            if dy >= 0:
                d.draw_hline(self.OX - half, y, 2 * half + 1, self.SECTOR)
            else:
                gap = int(-dy * cut)
                if gap < half:
                    d.draw_hline(self.OX - half, y, half - gap, self.SECTOR)
                    d.draw_hline(self.OX + gap + 1, y, half - gap, self.SECTOR)
        self.draw_grid()
        self.draw_legend()

    def draw_grid(self):
        d = self.display
        for r in self.ring_px:
            steps = int(r * 2 * self.edge) + 1
            for s in range(steps + 1):
                a = -self.edge + 2 * self.edge * s / steps
                d.draw_pixel(round(self.OX + r * math.sin(a)), round(self.OY - r * math.cos(a)), self.GRID)
        for a in (-self.edge, self.edge):
            d.draw_line(self.OX, self.OY, round(self.OX + self.R * math.sin(a)), round(self.OY - self.R * math.cos(a)), self.GRID)
        d.draw_vline(self.OX, self.OY - self.R, self.R, self.GRID)
        d.fill_circle(self.OX, self.OY, 3, self.TEXT)

    def draw_labels(self):
        for r, m in zip(self.ring_px, self.RINGS):
            self.display.draw_text8x8(self.OX + 4, round(self.OY - r) + 3, str(m // 1000) + "m", self.GRID, self.SECTOR)

    def draw_legend(self):
        d = self.display
        d.draw_text8x8(232, 228, "R1", self.RADAR1, self.BLACK)
        d.draw_text8x8(260, 228, "R2", self.RADAR2, self.BLACK)
        d.draw_text8x8(288, 228, "LD", self.LIDAR, self.BLACK)

    def bg_pixel(self, px, py):
        dx = px - self.OX
        dy = self.OY - py
        r = math.sqrt(dx * dx + dy * dy)
        if r <= 3:
            return self.TEXT
        if r > self.R + 0.5:
            return self.BLACK
        a = abs(math.atan2(dx, dy))
        if abs(a - self.edge) < 0.5 and r * abs(math.sin(a - self.edge)) < 0.7:
            return self.GRID
        if a > self.edge:
            return self.BLACK
        if dx == 0 and dy > 0:
            return self.GRID
        for rp in self.ring_px:
            if abs(r - rp) < 0.6:
                return self.GRID
        return self.SECTOR

    def erase(self, x, y):
        s = self.DOT
        x0 = max(x - s, 0)
        y0 = max(y - s, 0)
        x1 = min(x + s, self.WIDTH - 1)
        y1 = min(y + s, self.HEIGHT - 1)
        buf = bytearray((x1 - x0 + 1) * (y1 - y0 + 1) * 2)
        k = 0
        for py in range(y0, y1 + 1):
            for px in range(x0, x1 + 1):
                c = self.bg_pixel(px, py)
                buf[k] = c >> 8
                buf[k + 1] = c & 0xFF
                k += 2
        self.display.block(x0, y0, x1, y1, buf)

    def to_screen(self, x, y, offset):
        if self.FLIP_X:
            x = -x
        d = math.sqrt(x * x + y * y)
        if d == 0 or d > self.MAX_RANGE:
            return None
        a = math.atan2(x, y) + math.radians(offset)
        return (round(self.OX + d * self.scale * math.sin(a)), round(self.OY - d * self.scale * math.cos(a)))

    def update(self, r1, r2, lidar):
        new = []
        for targets, offset, color in ((r1, -self.RADAR_OFFSET, self.RADAR1), (r2, self.RADAR_OFFSET, self.RADAR2)):
            for t in targets or []:
                p = self.to_screen(t[0], t[1], offset)
                if p:
                    new.append((p[0], p[1], color))
        if lidar:
            p = self.to_screen(0, lidar * 10, 0)
            if p:
                new.append((p[0], p[1], self.LIDAR))
        for x, y, c in self.dots:
            self.erase(x, y)
        for x, y, c in new:
            self.display.fill_circle(x, y, self.DOT, c)
        self.dots = new
        self.draw_labels()

    def draw_status(self, sensor_batt, local_batt, lidar, link, count):
        d = self.display
        s1 = f"SENS {sensor_batt:.2f}V" if sensor_batt else "SENS --.--V"
        s1 += f"   DISP {local_batt:.2f}V"
        s2 = f"LIDAR {lidar}cm" if lidar else "LIDAR ---"
        s2 += f"   TARGETS {count}"
        d.draw_text8x8(4, 4, s1 + " " * (39 - len(s1)), self.TEXT, self.BLACK)
        d.draw_text8x8(4, 16, s2 + " " * (39 - len(s2)), self.TEXT, self.BLACK)
        if link:
            d.draw_text8x8(4, 228, "LINK OK", self.OK, self.BLACK)
        else:
            d.draw_text8x8(4, 228, "NO LINK", self.WARN, self.BLACK)

VBattADC = ADC(Pin(1))
VBattADC.atten(ADC.ATTN_11DB)
Vbatt = 2 * ((VBattADC.read_u16() / 65535) * 3.3)

spi = SPI(1, baudrate=40000000, sck=Pin(6), mosi=Pin(7), miso=Pin(5))
display = Display(spi, dc=Pin(4), cs=Pin(10), rst=Pin(3), width=320, height=240, rotation=90)
screen = RadarScreen(display)

sta = network.WLAN(network.WLAN.IF_STA)  
sta.active(True)

e = espnow.ESPNow()
e.active(True)
peer = b'\x88V\xa6\\;\xf0'   # MAC address of peer's wifi interface, run print(sta.config('mac')) to find it
e.add_peer(peer)      

i = 0
fails = 0
link = False
data = {}
e.send(peer, "Starting...")
while True:
    host, msg = e.recv(500)
    while msg:
        h2, m2 = e.recv(0)
        if not m2:
            break
        host, msg = h2, m2
    Vbatt = 2 * ((VBattADC.read_u16() / 65535) * 3.3)
    if msg and host == peer:
        try:
            parsed = json.loads(msg.decode())
        except Exception:
            parsed = None
        if isinstance(parsed, dict):
            data = parsed
            i += 1
            sent = e.send(peer, str(i))
            fails = 0
            link = True
            screen.update(data.get("r1"), data.get("r2"), data.get("l"))
    else:
        fails += 1
        if fails >= 5:
            link = False
            print ("ESP32 Is not responding")
    count = len(data.get("r1") or []) + len(data.get("r2") or [])
    screen.draw_status(data.get("b"), Vbatt, data.get("l"), link, count)