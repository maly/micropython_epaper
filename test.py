"""
	Example for 4.2 inch black & white Good Display GDEQ042T81 E-ink screen
	Run on ESP32 / ESPink
"""

import epaper4in2
from machine import Pin, SPI
from time import sleep_ms

# SPIV on ESP
sck = Pin(18)
miso = Pin(19)
mosi = Pin(23)

# ESPink specific
dc = Pin(17)
cs = Pin(5)
rst = Pin(16)
busy = Pin(4)
spi = SPI(2, baudrate=2000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)

# ESPink power saving
epd_power = Pin(2, Pin.OUT)
epd_power.on()
sleep_ms(10)

e = epaper4in2.EPD(spi, cs, dc, rst, busy)

e.pwr_on()
e.init()

w = 400
h = 300
x = 0
y = 0

# --------------------

# use a frame buffer
# 400 * 300 / 8 = 15000
import framebuf
buf = bytearray(w * h // 8)
fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HMSB)
black = 0
white = 1
fb.fill(white)

# --------------------

# write hello world with black bg and white text
from image_dark import hello_world_dark
from image_light import hello_world_light
print('Image dark')
bufImage = hello_world_dark
fbImage = framebuf.FrameBuffer(bufImage, 128, 296, framebuf.MONO_HLSB)
fb.blit(fbImage, 140, 2)
bufImage = hello_world_light
fbImage = framebuf.FrameBuffer(bufImage, 128, 296, framebuf.MONO_HLSB)
fb.blit(fbImage, 288, 2)
fb.text("Hola heja",10,10,black)
ln = 50*100
buf[ln+0]=255
buf[ln+1]=0
buf[ln+2]=255
buf[ln+3]=0
buf[ln+4]=0
buf[ln+5]=0
buf[ln+1+50]=15

e.display_frame(buf)