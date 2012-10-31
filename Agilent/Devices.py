
import SCPI as _SCPI

class AgilentDeviceError(RuntimeError):
    pass


class _ATBaseLAN(object):

    def __init__(self, hostname, debug=False):

        self._debug = bool(debug)
        self._debug_verbose = debug > 1
        self._SCPI = _SCPI.SCPI(hostname, 5025, self._debug_verbose)

        ident = self._SCPI.query('*IDN?\n')
        self._DNUM = ident.split(',')[1]

        if self._debug:
            print 'Connected to:\n   ', ident
        if hasattr(self, 'DEVSTR'):
            if self._DNUM != self.DEVSTR:
                raise AgilentDeviceError('Wrong Agilent device! '
                                 'Connected to a %s' % self._DNUM)

    def SCPI_send_cmd(self, cmd):
        self._SCPI.send('%s\n' % str(cmd))
        return

    def SCPI_query_cmd(self, cmd):
        answer = self._SCPI.query('%s\n' % str(cmd))
        return answer
    
    def _print_debug(self, msg):
        if self._debug:
            print 'DBG:%s> %s' % (self._DNUM, str(msg))



class AT53220A(_ATBaseLAN):
    """
    Agilent Frequency Counter/Timer 53220A Device Class

    parameters:
        * hostname str > ip or hostname
        * debug > True - normal | 2 - verbose

    """
    DEVSTR = '53220A'

    def input(self, channel, coupling='DC', filter_=False, impedance=50, 
            noisereject=False, probe=1):
        pass


    def input_get(self):
        ret = {}
        for inp in ['INP1','INP2']:
            conf = {'coupling'   : self.SCPI_query_cmd(inp+':COUP?'),
                    'lpfilter'   : self.SCPI_query_cmd(inp+':FILT?'),
                    'impedance'  : self.SCPI_query_cmd(inp+':IMP?'),
                    'level'      :(self.SCPI_query_cmd(inp+':LEV1?'),
                                   self.SCPI_query_cmd(inp+':LEV2?')),
                    'nreject'    : self.SCPI_query_cmd(inp+':NREJ?'),
                    'probe'      : self.SCPI_query_cmd(inp+':PROB?'),
                    'protection' : self.SCPI_query_cmd(inp+':PROT?'),
                    'range'      : self.SCPI_query_cmd(inp+':RANG?'),
                    'slope'      :(self.SCPI_query_cmd(inp+':SLOP1?'),
                                   self.SCPI_query_cmd(inp+':SLOP2?')) }
            ret[inp] = conf
        return ret

    def display_text(self, msg):
        self.SCPI_send_cmd('DISP:TEXT "%s"' % msg.replace("'",''))

    def display_mode(self, mode='numeric'):
        """
        numeric,
        histogram,
        tchart
        """
        self.SCPI_send_cmd('DISP:MODE %s' % str(mode))

    def display_enable(self, state):
        state = ['OFF', 'ON'][bool(state)]
        self.SCPI_send_cmd('DISP %s' % state)

        

class AT34410A(_ATBaseLAN):
    """
    Agilent Multimeter 34410A Device Class

    parameters:
        * hostname str > ip or hostname
        * debug > True - normal | 2 - verbose

    """
    DEVSTR = '34410A'


