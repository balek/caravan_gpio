#!/usr/bin/env python

import os.path

from twisted.internet.defer import inlineCallbacks, Deferred
from autobahn.twisted.util import sleep

from caravan.base import VanSession, VanDevice, deviceCommand, VanModule, Bool, Decimal, Int



GPIO_PATH = '/sys/class/gpio'


class Pin(VanDevice):
    list = None
    vfile_mode = 'r'

    def __init__(self, parent, name, pin):
        super(Pin, self).__init__(parent, name)
        self.path = os.path.join(GPIO_PATH, 'gpio%i' % pin)
        if not os.path.exists(self.path):
            export_file = open(os.path.join(GPIO_PATH, 'export'), 'w')
            export_file.write(str(pin))
            export_file.close()
        self.vfile = open(os.path.join(self.path, 'value'), self.vfile_mode)


class Output(Pin):
    vfile_mode = 'w'
    sleeping = None

    def __init__(self, parent, name, pin):
        super(Output, self).__init__(parent, name, pin)
        direction_file = open(os.path.join(self.path, 'direction'), 'w')
        direction_file.write('out')
        direction_file.close()

    @deviceCommand(Bool())
    @inlineCallbacks
    def set(self, value):
        if self.sleeping and not self.sleeping.called:
            self.sleeping.cancel()
            yield sleep(0.1)
        self.vfile.write(str(int(value)))
        self.vfile.flush()
        self.changeState(value)

    @deviceCommand(Decimal(min=0, precision=2))
    @inlineCallbacks
    def hold(self, duration):
        yield self.set(True)
        self.sleeping = sleep(duration)
        try:
            yield self.sleeping
        finally:
            yield self.set(False)


class GPIOModule(VanModule):
    @deviceCommand(Int(1))
    def createOutput(self, pin):
        Output(self, 'pin%i' % pin, pin)


class AppSession(VanSession):
    def start(self):
        GPIOModule(self, 'gpio')
