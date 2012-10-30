"""
Some Phidgets Wrappers
"""

import collections
import sys

import Phidgets.Devices.InterfaceKit
import Phidgets.PhidgetException


def onPanic(panicfunc):
    """decorator: call panicfunc on RuntimeError or PhidgetException"""
    def onPanicDecorator(function):
        def wrapped(self, *args):
            try:
                ret = function(self, *args)
                return ret
            except RuntimeError, Phidgets.PhidgetException.PhidgetException:
                panicfunc(self)
        return wrapped
    return onPanicDecorator


class SimpleInterfaceKit888(object):

    def __init__(self, serial=148921, debug=False):
        self._debug = bool(debug)

        self.kit = self._connect_phidget(serial)
        # callbacks are stored here
        self._cb = collections.OrderedDict()
        # connect callbacks
        self.kit.setOnInputChangeHandler(self._cb_handler)
        # old state
        self._oldstate = self.getInputs()


    def _connect_phidget(self, serial): #, host): not used yet
        # open and load the Phidget InterfaceKit
        try:
            kit = Phidgets.Devices.InterfaceKit.InterfaceKit()
            kit.openPhidget(serial)
        except RuntimeError, Phidgets.PhidgetException.PhidgetException:
            raise
        # wait for the device to attach
        try:
            kit.waitForAttach(2000)
        except Phidgets.PhidgetException.PhidgetException:
            raise
        return kit


    def _cb_handler(self, caller):
        if self._cb:
            newstate = self.getInputs()
            changed = self._oldstate ^ newstate 
            self._oldstate = newstate
            for mask, cb in self._cb.iteritems():
                if changed & mask:
                    cb(caller)


    def getInputs(self):
        """
        get all Inputs as a integer
        """
        
        out = 0
        for i in range(8):
            d = self.kit.getInputState(i)
            out += d<<i
        return out


    def setOutputs(self, out, mask=0xFF):
        """
        set outputs. mask bits that shouldn't be changed.
        """
        for i in range(8):
            if (mask>>i)&0x01:
                self.kit.setOutputState(i, bool((out>>i)&0x01))


    def setOnChangeCallback(self, func, mask=0xFF):
        """
        add callback functions dependend on which inputs have changed.
        each mask is only available once.
        order of added function = order of execution (if masked correct).
        """
        if not (func is None or hasattr(func, '__call__')):
            raise TypeError('OnChangeCallback is not callable')
        mask &= 0xFF
        self._cb[mask] = func





