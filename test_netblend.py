import struct
import netblend

class VersionInfo(netblend.Type):
	def __str__(self):
		return 'blender_version : ' + str(self.blender_version) + '\n' + \
			'netblend_version: ' + str(self.netblend_version)
	
	def __init__(self, blender_version = 0, netblend_version = 0):
		self.blender_version = blender_version
		self.netblend_version = netblend_version
	
	@staticmethod
	def size():
		return struct.calcsize('=ii')
	
	def pack(self, nb):
		return struct.pack('=ii', self.blender_version, self.netblend_version)
	
	def unpack(self, b, nb):
		self.blender_version, self.netblend_version = struct.unpack('=ii', b)

class AdditionalInfo(netblend.MutableType):
	def __str__(self):
		return 'the info is: ' + self.string
	
	def __init__(self, s = None):
		self.string = s
	
	def size(self):
		return len(self.string.encode())
	
	def pack(self, nb):
		return self.string.encode()
	
	def unpack(self, b, nb):
		self.string = b.decode()

class StrayLinker(netblend.Type):
	def __str__(self):
		return 'the stray is a ' + ('nothing' if not self.addi else self.addi.__class__.__name__) + ' at ' + ('nowhere' if not self.addi else str(id(self.addi)))
	
	def __init__(self, o = None):
		self.addi = o
	
	@staticmethod
	def size():
		return netblend.idsize
	
	def pack(self, nb):
		return nb(self.addi)
	
	def unpack(self, b, nb):
		self.addi = nb(b)
	
	def walk(self):
		if self.addi:
			yield self.addi
		raise StopIteration

class SimpleType(netblend.Type):
	@staticmethod
	def size():
		return 0
	
	def pack(self, n):
		return bytes()
	
	def unpack(self, n, nb):
		pass

defs = [SimpleType, VersionInfo, AdditionalInfo, StrayLinker]

print('creating netblend')
n = netblend.NetBlend()

print('creating simple object')
o = VersionInfo(256, 1)

print('adding object to netblend')
n.add(o)

print('creating advanced object')
o = AdditionalInfo("I am a string, you know?")

print('adding advanced to netblend')
n.add(o)

print('creating and adding a StrayLinker to the advanced object')
o = StrayLinker(o)
n.add(o)

print('O__O adding a stray object!')
o = SimpleType()

print('adding a StrayLinker to the O__O stray')
o = StrayLinker(o)
n.add(o)

print('adding lots of empty types')
for i in range(5):
	o = SimpleType()
	n.add(o)

print('adding circlic dependancy')
o = StrayLinker()
o.addi = o
n.add(o)

print('saving netblend as test.netblend')
with open('test.netblend', 'wb+') as f:
	n.write(defs, f)

print('cleaning up')
del n
del o

print('opening test.netblend as a netblend')
n = netblend.open(defs, 'test.netblend')

print('printing objects')
for o in n.walk():
	print(' \033[1;33m' + o.__class__.__name__ + '\033[0m' + ' @ ' + str(id(o)))
	print(o)

print('')
