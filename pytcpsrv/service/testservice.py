#coding=UTF-8

class testservice(object):

	def getuser(self):
		uid = self.bufferReq.uid
		self.bufferRsp.uid = uid
		self.bufferRsp.name = "aison"
		self.bufferRsp.age = 30
		self.bufferRsp.city = "shenzhen"
		return self.bufferRsp.SerializeToString()
