#! /usr/bin/env python
#coding=utf-8

import importlib
import struct
import socket

from pytcpsrv import protolist

msgId = 1
buffNameReq = protolist.protolist(msgId)

proto_module = importlib.import_module('pytcpsrv.proto.test_pb2')
classReq = getattr(proto_module,buffNameReq)
objReq = classReq()

objReq.uid = 10001
sreialStr = objReq.SerializeToString()
length = len(sreialStr)+4
data = struct.pack(">H",msgId)+struct.pack(">H",length)+sreialStr+"\n"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 8888))

sock.send(data)
res = sock.recv(1024)
msgId = struct.unpack(">H",res[0:2])[0]
length = struct.unpack(">H",res[2:4])[0]
buffData = res[4:length]
buffNameRsp = protolist.protolist(msgId)
classRsp = getattr(proto_module,buffNameRsp)
objRsp = classRsp()
objRsp.ParseFromString(buffData)
print objRsp
sock.close()