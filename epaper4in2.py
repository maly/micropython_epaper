"""
MicroPython Good Display GDEQ042T81 (GDEY042T81)

Based on MicroPython Waveshare 4.2" Black/White GDEW042T2 e-paper display driver
https://github.com/mcauser/micropython-waveshare-epaper

licensed under the MIT License
Copyright (c) 2017 Waveshare
Copyright (c) 2018 Mike Causer
"""

"""
MicroPython Good Display GDEQ042T81 (GDEY042T81) e-paper display driver

MIT License
Copyright (c) 2024 Martin Maly

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
from time import sleep_ms

# Display resolution
EPD_WIDTH  = const(400)
EPD_HEIGHT = const(300)
BUSY = const(0)  # 0=busy, 1=idle

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.powered = False
        self.init_done = False
        self.hibernate = True
        self.use_fast_update = True

    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)
        
    def _ndata(self, data):
        self._data(bytearray([data]))
        
    def pwr_on(self):
        if self.powered == False:
            self._command(0x22, b'\xe0')
            self._command(0x20)
            self.wait_until_idle()
            self.powered = True

    def pwr_off(self):
        if self.powered == True:
            self._command(0x22, b'\x83')
            self._command(0x20)
            self.wait_until_idle()
            self.powered = False

    #set partial
    def set_partial(self, x, y, w, h):
        self._command(0x11,b'\x03')
        self._command(0x44)
        self._ndata(x // 8)
        self._ndata((x + w - 1) // 8)
        self._command(0x45)
        self._ndata(y % 256)        
        self._ndata(y // 256)
        self._ndata((y+h-1) % 256)
        self._ndata((y+h-1) // 256)
        self._command(0x4E)
        self._ndata(x // 8)
        self._command(0x4F)
        self._ndata(y % 256)        
        self._ndata(y // 256)

    def init(self):
        if self.hibernate==True:
            self.reset()
        sleep_ms(100)
        #self.wait_until_idle()
        self._command(const(0x12)) #SWRESET
        self.wait_until_idle()
        
        self._command(0x01,b'\x2B\x01\x00') #MUX
        self._command(0x21,b'\x40\x00')
        self._command(0x3C,b'\x05')  #BorderWaveform
        self._command(0x18,b'\x80') #ReadTempSensor
        
        self.set_partial(0, 0, self.width, self.height)
        self.init_done = True

    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            sleep_ms(100)
            print("Wait till idle")

    def reset(self):
        self.rst(0)
        sleep_ms(200)
        self.rst(1)
        sleep_ms(200)

    def update_full(self):
        #update Full
        print("Do Update")
        self._command(0x21,b'\x40\x00')
        if self.use_fast_update == False:
            self._command(0x22,b'\xf7')
        else:
            self._command(0x1A, b'\x64')
            self._command(0x22,b'\xd7')
        self._command(0x20)
        self.wait_until_idle()
        print("Updated", self.busy.value())

    def write_image(self, command, bitmap, mirror_x, mirror_y):
        sleep_ms(1)
        h = self.height
        w = self.width
        bpl = w // 8 # bytes per line
        
        self._command(command)
        for i in range(0, h):
            for j in range(0, bpl):
                idx = ((bpl-j-1) if mirror_x else j) + ((h-i-1) if mirror_y else i) * bpl
                self._ndata(bitmap[idx])
                
    def write_value(self, command, value):
        sleep_ms(1)
        h = self.height
        w = self.width
        bpl = w // 8 # bytes per line
        
        self._command(command)
        for i in range(0, h):
            for j in range(0, bpl):
                self._ndata(value)


    # draw the current frame memory
    def display_frame(self, frame_buffer):
        print("disfr")
        if self.init_done==False:
            self.init()

        self.set_partial(0, 0, self.width, self.height)
        
        #self.write_value(0x26, 0xff) # RED is 1
        self.write_image(0x24, frame_buffer, True, True)

        self.update_full()


    # to wake call reset() or init()
    def sleep(self):
        self.pwr_off()
        self._command(0x10, b'\x01')
        self.init_done = False
        self.hibernate = True
