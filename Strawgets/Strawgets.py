"""
Some Phidgets Wrappers
"""

import collections
import sys
import time

import Phidgets.Devices.InterfaceKit
import Phidgets.Devices.Stepper
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


class SyringeStepper(object):

    def __init__(self, serial=267333, debug=False):
        self._debug = bool(debug)

        self.stp = self._connect_phidget(serial)
        # callbacks are stored here
        #self._cb = collections.OrderedDict()
        # connect callbacks
        self.setup_motor()

        self.maxpos = 340362
        self._CALIB = False
        self.calibrate()

    def _connect_phidget(self, serial): #, host): not used yet
        # open and load the Phidget InterfaceKit
        try:
            stp = Phidgets.Devices.Stepper.Stepper()
            stp.openPhidget(serial)
        except RuntimeError, Phidgets.PhidgetException.PhidgetException:
            raise
        # wait for the device to attach
        try:
            stp.waitForAttach(2000)
        except Phidgets.PhidgetException.PhidgetException:
            raise
        return stp

    def setup_motor(self):
        self.stp.setCurrentLimit(0, 1.68)
        self.stp.setVelocityLimit(0, 20000.)
        self.stp.setEngaged(0, True)
        if self._debug: print "SyringeStepper: Motor engaged."

    def isAtEndpoint(self):
        # inverted logic due to the leftover switch that's being used
        atEnd = not self.stp.getInputState(0)
        if self._debug: print "SyringeStepper: %sat Endpoint." % (
                                              ['not ',''][atEnd] )
        return atEnd

    def calibrate(self):
        self._CALIB = True
        if not self.isAtEndpoint():
            if self._debug: print "SyringeStepper: Calibrating."
            self.stp.setOnInputChangeHandler(self._calibrate_endpoint)
            self.stp.setTargetPosition(0, self.stp.getPositionMin(0))
            while self._CALIB:
                time.sleep(0.1)
        else:
            self.start = self.stp.getCurrentPosition(0)
            self._CALIB = False

    def _calibrate_endpoint(self, caller=None):
        if self.isAtEndpoint():
            pos = self.stp.getCurrentPosition(0)
            self.stp.setTargetPosition(0, pos)
            self.start = pos
            self._CALIB = False
            return
        else:
            # leaving the startpos
            return

    def _nonlinearCorrection(self, ml):
        # The Pump has to be calibrated in this function
        # quick and dirty for now:
        # start = 0 > 0.385ml
        # endpt = 8599 > 0.0ml
        return int(ml*(self.maxpos-1)/0.36)

    def inject(self, val):
        val = self._nonlinearCorrection(val)
        cur = self.stp.getCurrentPosition(0)
        if cur - self.start + val < self.maxpos:
            self.stp.setTargetPosition(0, cur+val)
        else:
            raise RuntimeError("SyringeStepper: Can't go that far!")

    def isAtTargetPos(self):
        cur = self.stp.getCurrentPosition(0)
        tar = self.stp.getTargetPosition(0)
        return cur - tar

