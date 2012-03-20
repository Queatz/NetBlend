import struct
import io

idsize = struct.calcsize('=I')

# Header definition

class Type:
	"Whether or not the bytes size can vary."
	_mutable = False
	
	@staticmethod
	def size():
		"Number of bytes returned by pack()."
		raise UserWarning('size must be implemented.')
	
	def unpack(self, b, nb):
		"Load from bytes."
		raise UserWarning('unpack must be implemented.')
	
	def pack(self, nb):
		"Bytes that will load this particular."
		raise UserWarning('pack must be implemented.')
	
	def walk(self):
		"Method to visit all objects that this one relies on."
		raise StopIteration

class MutableType(Type):
	_mutable = True

	def size(self):
		"Number of bytes returned by pack()."
		return len(self.pack(lambda i: struct.pack('=I', 0)))

# File conglomerate

class NetBlend:
	"A compact and minimal blend format."
	@staticmethod
	def _types_id(structs, struct):
		try:
			return structs.index(struct if type(struct) == type else type(struct)) + 1
		except ValueError:
			raise EnvironmentError('Bad structs list for file')
	@staticmethod
	def _types_ty(structs, struct):
		try:
			return structs[struct - 1]
		except IndexError:
			raise EnvironmentError('Bad structs list for file')
	
	def __init__(self):
		"Create a NetBlend using the given list of structs."
		self.objects = []
	
	def add(self, o):
		"Add a global object."
		self.objects.append(o)
	
	def remove(self, o):
		"Remove a global object."
		self.objects.remove(o)
	
	def walk(self):
		"All objects that will be saved."
		
		visited = []
		
		def visit(o):
			if o in visited:
				raise StopIteration
			yield o
			visited.append(o)
			
			for oo in o.walk():
				for ooo in visit(oo):
					yield ooo
		
		for o in self.objects:
			for oo in visit(o):
				yield oo
	
	def read(self, types, stream):
		"Read a stream into the netblend."
		t = None
		
		typeheadersize = struct.calcsize('=HI')
		typevarysize = struct.calcsize('=I')
		
		_loadid = {}
		idc = 0
		ranges = []
		
		# Read header
		while True:
			vvv = stream.read(typeheadersize)
			if not vvv:
				break
			
			r = struct.unpack('=HI', vvv)
			
			# Header end is a (0, 0)
			if r[0] < 1:
				break
			
			if self._types_ty(types, r[0])._mutable:
				vr = list()
				for i in range(r[1]):
					vr.append(struct.unpack('=I', stream.read(typevarysize))[0])
				ranges.append(vr)
			else:
				ranges.append(r)
			
			for i in range(r[1]):
				o = self._types_ty(types, r[0])()
				idc += 1
				_loadid[idc] = o
				
				# Put in global objects
				# It will save no matter what this way
				self.objects.append(o)
		
		# Read data
		
		def fromID(i):
			i = struct.unpack('=I', i)[0]
			if i == 0:
				return None
			if i not in _loadid:
				raise EnvironmentError('Lookup of object not found.')
			return _loadid[i]
			
		
		idc = 0
		
		for r in ranges:
			if isinstance(r, tuple):
				s = self._types_ty(types, r[0]).size()
				for i in range(r[1]):
					idc += 1
					_loadid[idc].unpack(stream.read(s), fromID)
			else:
				for s in r:
					idc += 1
					_loadid[idc].unpack(stream.read(s), fromID)
	
	def write(self, types, stream):
		"Write the netblend to a stream."
		ol = sorted(list(self.walk()), key = lambda o: self._types_id(types, o))
		
		if len(ol) < 1:
			return

		i = 0
		t = None
		batch = None
		
		_saveid = {}
		
		def write_batch():
			if not batch: return
			stream.write(struct.pack('=HI', batch[0], batch[1]))
			if batch[2]:
				stream.write(struct.pack('=' + str(len(batch[2])) + 'I', *batch[2]))
		
		# Write the header
		for o in ol:
			if type(o) != t:
				# Write last batch
				write_batch()
					
				# Start new batch
				batch = [self._types_id(types, o), 0, []]
				t = type(o)
			
			# If the struct is a varying sized type then we write each size.
			# Otherwise we write nothing, as the sizes are already known.
			if type(o)._mutable:
				batch[2].append(o.size())
			
			# Increment batch count
			batch[1] += 1
			
			# ID counter
			i += 1
			_saveid[id(o)] = i
		
		# Write last batch
		write_batch()
		
		# 0 = End of Header
		stream.write(struct.pack('=HI', 0, 0))
		
		def toID(o):
			if o is None:
				return struct.pack('=I', 0)
			if id(o) not in _saveid:
				raise EnvironmentError('Lookup of object not found.  The object requested either wasn\'t added or is missing in a walk().')
			return struct.pack('=I', _saveid[id(o)])
		
		# Write the raw data
		for o in ol:
			stream.write(o.pack(toID))

# Convenience

def open(defs, filename):
	b = NetBlend()
	a = io.open(filename, 'rb')
	b.read(defs, a)
	a.close()
	return b
