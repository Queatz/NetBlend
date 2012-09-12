import struct
import io

ID_SIZE = struct.calcsize('=I')
TP_SIZE = struct.calcsize('=H')

import glm
from .standard import defs

class Node:
	_nb_type = ''

class NetBlend(list):
	
	_types = [
		type(None),
		object,
		list,
		str,
		bytes,
		int,
		float,
		glm.vec2,
		glm.vec3,
		glm.vec4,
	]
	
	_types = {i: x for i, x in enumerate(_types)}
	
	for x in range(len(_types)):
		_types[_types[x]] = x
	
	def load(self, file, map = -1):
		"Load nodes into this netblend from a file or stream. A list can be supplied to the second argument to map types to classes."
		if map == -1:
			map = {x._nb_type: x for x in defs}
		
		if isinstance(file, str):
			file = io.open(file, 'rb')
		
		# Skip header and version
		file.seek(16)
		
		# Just a reference of how many objects are already in
		offset = len(self)

		# Load objects
		
		def readID():
			d = file.read(ID_SIZE)
			if not d:
				return -1
			return struct.unpack('=I', d)[0]
		
		def readType():
			d = file.read(TP_SIZE)
			if not d:
				return -1
			return struct.unpack('=H', d)[0]
		
		readUInt = readID
		
		def link(i):
			return self[offset + i - 1]
		
		def read(t):
			t = self._types[t]
			
			if t is type(None):
				return None
			elif t is object:
				i = readID()
				
				if i < 1:
					return None
				else:
					return link(i)
			elif t is list:
				i = readUInt()
				if i < 1:
					return []
				else:
					t = readType()
					r = []
					for x in range(i):
						n = read(t)
						r.append(n)
					
					return r
			elif t is str:
				return file.read(readUInt()).decode()
			elif t is bytes:
				return file.read(readUInt())
			elif t is int:
				return struct.unpack('=i', file.read(struct.calcsize('=i')))[0]
			elif t is float:
				return struct.unpack('=f', file.read(struct.calcsize('=f')))[0]
			elif t is bool:
				return bool(struct.unpack('=B', file.read(struct.calcsize('=B'))[0]))
			elif t in (glm.vec2, glm.vec3, glm.vec4):
				return t(file.read(len(bytes(t()))))
		
		while True:
			i = readType()
			
			if i == -1 or i == self._types[type(None)]:
				break
			
			nbt = read(i)
			o = None
			
			if map and nbt in map:
				o = map[nbt]()
				if not hasattr(o, '_nb_type') or o._nb_type != nbt:
					o._nb_type = nbt
			
			if not o:
				o = Node()
				o._nb_type = nbt
			
			self.append(o)
		
		on = offset
		while True:
			i = readType()
			
			if i == -1:
				break
		
			if i == self._types[type(None)]:
				on += 1
				continue
			
			a = read(i)
			setattr(self[on], a, read(readType()))
		
		file.close()
		
		return self
	
	def save(self, file):
		"Write the netblend to a file or stream."
		if isinstance(file, str):
			file = io.open(file, 'wb+')
		
		# Discover objects
		
		objs = []
		
		def walk(o):
			if o in objs:
				return
			
			objs.append(o)
			
			for a in dir(o):
				if a.startswith('_'):
					continue
				oo = getattr(o, a)
				if hasattr(oo, '_nb_type'):
					walk(oo)
				elif isinstance(oo, list) or isinstance(oo, tuple) or isinstance(oo, set):
					for b in oo:
						if hasattr(oo, '_nb_type'):
							walk(b)
		
		for x in self:
			walk(x)
		
		# Write signature
		file.write('.NETBLEND\000\000\000\007\000\004'.encode())
		
		# Write version
		file.write(struct.pack('=B', 1))
		
		# Save objects
		
		def idd(o):
			if o is None:
				return struct.pack('=I', 0)
			
			try:
				return struct.pack('=I', objs.index(o)+1)
			except ValueError:
				return struct.pack('=I', 0)
		
		def write(v = TypeError, incl_typ = True):
			if v is TypeError:
				file.write(struct.pack('=H', 0))
				return
			else:
				t = self.typeOf(v)
				
				if incl_typ:
					file.write(struct.pack('=H', self._types[t]))
			
			if t is object:
				i = idd(v)
				file.write(i)
			elif t is list:
				if len(v) < 1:
					file.write(struct.pack('=I', 0))
				else:
					lt = self.typeOf(v[0])
					
					# Allow an int to be in a float list
					if lt == int:
						for x in v:
							if type(x) != int:
								lt = float
								break
					
					# None == no object
					if lt == type(None):
						lt = object
					
					file.write(struct.pack('=I', len(v)))
					file.write(struct.pack('=H', self._types[lt]))
					
					for x in v:
						write(x, False)
			elif t is str:
				b = v.encode()
				file.write(struct.pack('=I', len(b)))
				file.write(b)
			elif t is bytes:
				file.write(struct.pack('=I', len(b)))
				file.write(b)
			elif t is int:
				file.write(struct.pack('=i', v))
			elif t is float:
				file.write(struct.pack('=f', v))
			elif t is bool:
				file.write(struct.pack('=B', 1 if v else 0))
			elif t in (glm.vec2, glm.vec3, glm.vec4):
				file.write(bytes(v))
			else:
				raise TypeError('Invalid type.')
		
		for x in objs:
			write(x._nb_type)
		
		write()
		
		for x in objs:
			for a in dir(x):
				if a.startswith('_'):
					continue
				xa = getattr(x, a)
				if hasattr(xa, '_nb_type') or type(xa) in (type(None), list, bool, tuple, set, float, int, bytes, str, glm.vec2, glm.vec3, glm.vec4):
					write(a)
					write(xa)
			write()
		
		file.close()
		
		return self
	
	def find(self, t):
		"Iterate all objects of a certain type."
		if isinstance(t, str):
			for x in self:
				if x._nb_type == t:
					yield x
		else:
			for x in self:
				if isinstance(x, t):
					yield x
		
		raise StopIteration
	
	@staticmethod
	def typeOf(v):
		"Get the type the netblend saves an object as.  Returns -1 on failure."
		t = type(v)
		if t is type(None) or hasattr(v, '_nb_type'):
			return object
		elif t in (list, set, tuple):
			return list
		elif t in (str, bool, bytes, int, float, glm.vec2, glm.vec3, glm.vec4):
			return t
		else:
			return -1

def open(f, m = -1):
	"Open a .netblend.  Same as NetBlend.load()."
	return NetBlend().load(f, m)
