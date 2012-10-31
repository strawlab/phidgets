import socket

class SCPI(object):
    def __init__(self, host, port, debug=False):
        self._debug = bool(debug)
        self._host = str(host)
        self._port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self._host, self._port))
        self._more = False

    def send(self, string):
        if self._debug: print "Dbg:SCPI:%s:%d:SEND> %s" % (self._host,
                                                           self._port, str(string))
        self.socket.send(str(string))

    def recieve(self):
        buff = ""
        while True:
            buff += self.socket.recv(4096)
            if buff[-1] == "\n":
                break
        if self._debug: print "Dbg:SCPI:%s:%d:RECV> %s" % (self._host,
                                                           self._port, str(buff))
        return buff[:-1]

    def query(self, cmd):
        self.send(cmd)
        return self.recieve()

