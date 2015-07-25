#! /usr/bin/env python
#coding=utf-8

import signal
import struct
import socket
import importlib

#import tornado.process
from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
from pytcpsrv import msgacts,protolist

def handle_signal(sig, frame):
    IOLoop.instance().add_callback(IOLoop.instance().stop)


class EchoServer(TCPServer):

    def handle_stream(self, stream, address):
        self._stream = stream
        self._stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self._stream.set_close_callback(self.on_disconnect)
        self._raddr = '%s:%d' % self._stream.socket.getpeername()
        self.on_connect()
        self._read_line()

    def _read_line(self):
        self._stream.read_until('\n',self._handle_read)

    
    def _handle_read(self, data):
        msgId = struct.unpack(">H",data[0:2])[0]
        length = struct.unpack(">H",data[2:4])[0]
        buffData = data[4:length]
        
        buffNameReq = protolist.protolist(msgId)
        buffNameRsp = protolist.protolist(msgId+1)

        moduleName = msgacts.msgAct[buffNameReq][0]
        className = msgacts.msgAct[buffNameReq][1]
        methodName = msgacts.msgAct[buffNameReq][2]

        proto_module = importlib.import_module('pytcpsrv.proto.'+moduleName+'_pb2')
        classReq = getattr(proto_module,buffNameReq)
        classRsp = getattr(proto_module,buffNameRsp)
        objReq = classReq()
        objRsp = classRsp()
        objReq.ParseFromString(buffData)

        service_module = importlib.import_module('pytcpsrv.service.'+className)
        classSrv = getattr(service_module,className)
        objSrv = classSrv()
        objSrv.bufferReq = objReq
        objSrv.bufferRsp = objRsp
        rspBufferData =  getattr(objSrv, methodName)()
        rspData =  struct.pack(">H",msgId+1)+struct.pack(">H",len(rspBufferData)+4)+rspBufferData+"\n"
        self._stream.write(rspData)
        self._read_line()

    def log(self, msg):
        print("%s" % msg)


    def on_connect(self):
        self.log('connected, %s' % self._raddr)

    def on_disconnect(self):
        self.log("disconnected, %s" % self._raddr)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    server = EchoServer()
    server.listen(8888)
    IOLoop.instance().start()
    IOLoop.instance().close()

    #sockets = tornado.tcpserver.bind_sockets(8888)
    #tornado.process.fork_processes(0)
    #server = EchoServer()
    #server.add_sockets(sockets)
    #IOLoop.instance().start()
    #IOLoop.instance().close()
   