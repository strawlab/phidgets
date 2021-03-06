
import SCPI as _SCPI
import numpy as _np

class AgilentDeviceError(RuntimeError):
    pass


class _ATBaseLAN(object):

    def __init__(self, hostname, debug=False, errorchecking=True):

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

    def SCPI_send_cmd(self, cmd, check=True):
        self._SCPI.send('%s\n' % str(cmd))
        if bool(check): self._check_error()
        return

    def SCPI_query_cmd(self, cmd, check=True):
        answer = self._SCPI.query('%s\n' % str(cmd))
        if bool(check): self._check_error()
        return answer
    
    def _print_debug(self, msg):
        if self._debug:
            print 'DBG:%s> %s' % (self._DNUM, str(msg))

    def _check_error(self):
        answer = self._SCPI.query('SYST:ERR?\n')
        n, s = answer.split(',', 1) 
        if int(n) != 0:
            raise AgilentDeviceError(answer)


class AT53220A(_ATBaseLAN):
    """
    Agilent Frequency Counter/Timer 53220A Device Class

    parameters:
        * hostname str > ip or hostname
        * debug > True - normal | 2 - verbose

    """
    DEVSTR = '53220A'

    def input(self, channel, coupling='AC', filter_='OFF', impedance=1.0e6, 
                autolevel='ON', level=('DEF','DEF'), nreject='OFF',
                probe='DEF', range_='DEF', slope='POS'):
        
        self.SCPI_send_cmd('INP%d:COUP %s' % (channel, coupling))     
        self.SCPI_send_cmd('INP%d:FILT %s' % (channel, filter_))     
        self.SCPI_send_cmd('INP%d:IMP %s'  % (channel, impedance))     
        self.SCPI_send_cmd('INP%d:LEV:AUTO %s' % (channel, autolevel))     
        self.SCPI_send_cmd('INP%d:LEV1 %s' % (channel, str(level[0])))     
        self.SCPI_send_cmd('INP%d:LEV2 %s' % (channel, str(level[1])))     
        self.SCPI_send_cmd('INP%d:NREJ %s' % (channel, nreject))     
        self.SCPI_send_cmd('INP%d:RANG %s' % (channel, range_))     
        self.SCPI_send_cmd('INP%d:SLOP %s' % (channel, slope))     


    def input_get(self):
        ret = {}
        for inp in ['INP1','INP2']:
            conf = {'coupling'   : self.SCPI_query_cmd(inp+':COUP?'),
                    'lpfilter'   : self.SCPI_query_cmd(inp+':FILT?'),
                    'impedance'  : self.SCPI_query_cmd(inp+':IMP?'),
                    'autolevel'  : self.SCPI_query_cmd(inp+':LEV:AUTO?'),
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


    def r_g(self, max_count=None, format_='ascii', byteorder='>'):
        """
        R? [<max_count>]
        """
        assert format_.lower() in ['ascii', 'real'], 'use format ascii or real'
        assert byteorder in ['>', '<'], ('specify ">" big endian (NORM)'
                                          ' or "<" little endian (SWAP)')
        # check if there is Data!
        if int(self.SCPI_query_cmd('DATA:POIN?', False)) < 1:
            return None
        
        cmd = "R?\n" if max_count is None else "R? %d\n" % int(max_count)
        self._SCPI.send(cmd)
        
        # now we should get the return message
        # this should be #XY*data\n
        nX = int(self._SCPI.socket.recv(2)[-1])
        if nX < 1:
            return None
        
        else:
            nData = int(self._SCPI.socket.recv(nX))
           
            recv_buff = []
            while True:
                
                if nData < 1:
                    break
                _recv_data = self._SCPI.socket.recv(nData)
                # This is quite mean:
                #   it can happen, that ...socket.recv(N)
                #   returns a string with len(str) < N !!!
                recv_buff.append(_recv_data)
                nData -= len(_recv_data)

            END = self._SCPI.socket.recv(1)
            if END != "\n":
                raise RuntimeError("Booo! Bad!")
           
            if format_ == 'ascii':
                return _np.fromstring(''.join(recv_buff), dtype=_np.float64, sep=',')
    
            else:
                dt = _np.dtype(_np.float64).newbyteorder(byteorder)
                return _np.frombuffer(''.join(recv_buff), dtype=dt)
                




    def _test_totalize(self):
        def setupinput(self):
            self.SCPI_send_cmd('INP1:COUP DC')
            self.SCPI_send_cmd('INP1:FILT OFF')
            self.SCPI_send_cmd('INP1:IMP 50')
            self.SCPI_send_cmd('INP1:LEV:AUTO OFF')
            self.SCPI_send_cmd('INP1:LEV1 2.2')
            self.SCPI_send_cmd('INP1:NREJ OFF')
            self.SCPI_send_cmd('INP1:PROB 1')
            self.SCPI_send_cmd('INP1:RANG 5.0')
            self.SCPI_send_cmd('INP1:SLOP1 POS')
        def setuptotalize(self):
            self.SCPI_send_cmd('FUNC "TOT 1"')
            self.SCPI_send_cmd('SAMP:COUN 1000000')
            self.SCPI_send_cmd('TOT:GATE:SOUR TIME')
            self.SCPI_send_cmd('TOT:GATE:TIME 0.1')
            self.SCPI_send_cmd('INIT')
        
        setupinput()
        setuptotalize()
        self.display_mode('tchart')


    def read(self):
        return self.SCPI_query_cmd('READ?')

    def fetch(self):
        return self.SCPI_query_cmd('FETC?')

    def abort(self):
        return self.SCPI_send_cmd('ABOR')

    def display_text(self, msg):
        self.SCPI_send_cmd('DISP:TEXT "%s"' % msg.replace("'",''))

    def display_mode(self, mode='numeric'):
        """
        numeric,
        histogram,
        tchart
        """
        self.SCPI_send_cmd('DISP:TEXT:CLE')
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

    def _temporary_resistance(self):
        return self.SCPI_query_cmd('MEAS:RES?')

