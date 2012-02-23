import netblend
import struct

class Vec3(netblend.Type):
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    @staticmethod
    def size():
        return struct.calcsize('=3f')
    
    def pack(self, nb):
        return struct.pack('=3f', self.x, self.y, self.z)
    
    def unpack(self, b, nb):
        self.x, self.y, self.z = struct.unpack('=3f', b)
    
    def __str__(self):
        return str(tuple((self.x, self.y, self.z)))

class Vec3_lowp(netblend.Type):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
    
    @staticmethod
    def tosh(f):
        return int(
            max(
                min(
                    f * (1 << 14),
                    (1 << 15)), -(1 << 15)))
    
    @staticmethod
    def tohf(s):
        return s / (1 << 14)
    
    @staticmethod
    def size():
        return struct.calcsize('=3h')
    
    def pack(self, nb):
        return struct.pack('=3h', self.tosh(self.x), self.tosh(self.y), self.tosh(self.z))
    
    def unpack(self, b, nb):
        self.x, self.y, self.z = struct.unpack('=3h', b)
        self.x = self.tohf(self.x)
        self.y = self.tohf(self.y)
        self.z = self.tohf(self.z)
    
    def __str__(self):
        return str(tuple((self.x, self.y, self.z)))

class Scene(netblend.MutableType):
    def __init__(self):
        self.name = 'Scene'
        self.camera = None
        self.objects = []
    
    def size(self):
        return len(self.name.encode()) + 1 + (1 + len(self.objects)) * netblend.idsize
    
    def pack(self, nb):
        d = self.name.encode() + b'\0' + nb(self.camera)
        for o in self.objects:
            d += nb(o)
        return d
    
    def unpack(self, b, nb):
        i = 0
        for x in b:
            if x == 0:
                break
            i += 1
        self.name = b[:i].decode()
        i += 1
        self.camera = nb(b[i:i+netblend.idsize])
        i += netblend.idsize
        for x in range(i, len(b), netblend.idsize):
            self.objects.append(nb(b[x:x+netblend.idsize]))
    
    def walk(self):
        if self.camera:
            yield self.camera
        
        for o in self.objects:
            yield o
    
    def __str__(self):
        return '      name: ' + repr(self.name) + '\n   objects: ' + ', '.join(repr(x.name) for x in self.objects)

class Object(netblend.MutableType):
    def __init__(self):
        self.name = 'Object'
        self.data = None
        self.parent = None
        self.location = Vec3()
        self.rotation = Vec3()
        self.scale = Vec3()
        #self.modifiers = []
    
    def size(self):
        return len(self.name.encode()) + netblend.idsize * 2 + Vec3.size() * 3
    
    def pack(self, nb):
        return (self.name.encode() +
            nb(self.data) +
            nb(self.parent) +
            self.location.pack(nb) +
            self.rotation.pack(nb) +
            self.scale.pack(nb))
    
    def unpack(self, b, nb):
        nend = len(b) - (netblend.idsize * 2 + Vec3.size() * 3)
        self.name = b[:nend].decode()
        
        p = nend; pn = p+netblend.idsize
        self.data = nb(b[p:pn])
        
        p = pn; pn = p+netblend.idsize
        self.parent = nb(b[p:pn])
        
        p = pn; pn = p + Vec3.size()
        self.location = Vec3()
        self.location.unpack(b[p:pn], nb)
        
        p = pn; pn = p + Vec3.size()
        self.rotation = Vec3()
        self.rotation.unpack(b[p:pn], nb)
        
        p = pn; pn = p + Vec3.size()
        self.scale = Vec3()
        self.scale.unpack(b[p:pn], nb)
    
    def walk(self):
        if self.data:
            yield self.data
        if self.parent:
            yield self.parent
    
    def __str__(self):
        return '      name: ' + repr(self.name) + '\n    parent: ' + ('None' if not self.parent else str(id(self.parent))) + '\n      data: ' + ('None' if not self.data else str(id(self.data))) + '\n  location: ' + str(self.location) + '\n  rotation: ' + str(self.rotation) + '\n     scale: ' + str(self.scale)

class Mesh(netblend.MutableType):
    def __init__(self):
        self.name = 'Mesh'
        self.vertices = []
        self.faces = []
        #self.shapekeys
        #self.texcoords
        #self.texture
        #self.materials
        #self.vertex_colors
    
    def size(self):
        f = 0
        fvs = struct.calcsize('=I')
        for face in self.faces:
            f += fvs * (len(face) + 1)
        return len(self.name.encode()) + 1 + struct.calcsize('=I') + Vec3.size() * len(self.vertices) + f
    
    def pack(self, nb):
        v = bytes()
        for vertex in self.vertices:
            v += vertex.pack(nb)
        
        f = bytes()
        fsep = struct.pack('=I', 0)
        for face in self.faces:
            for vert in face:
                f += struct.pack('=I', self.vertices.index(vert) + 1)
            f += fsep
        
        return self.name.encode() + b'\0' + struct.pack('=I', len(self.vertices)) + v + f
    
    def unpack(self, b, nb):
        i = 0
        for x in b:
            if x == 0:
                break
            i += 1
        self.name = b[:i].decode()
        i += 1
        
        Isize = struct.calcsize('=I')
        vertcount, = struct.unpack('=I', b[i:i+Isize])
        i += Isize
        Vsize = Vec3.size()
        for x in range(i, i + vertcount * Vsize, Vsize):
            vv = Vec3()
            vv.unpack(b[x:x+Vsize], nb)
            self.vertices.append(vv)
        i += vertcount * Vsize
        
        FVsize = Isize
        collectv = []
        for x in range(i, len(b), FVsize):
            i, = struct.unpack('=I', b[x:x+FVsize])
            if i == 0:
                self.faces.append(collectv)
                collectv = []
            else:
                collectv.append(self.vertices[i - 1])
            
    
    def __str__(self):
        return '      name: ' + repr(self.name) + '\n  vertices: ' + str(len(self.vertices)) + '\n     faces: ' + str(len(self.faces))

# Always add to the end for backwards compatibility
# (type id is based on index in the list)
defs = [
    Vec3,
    Scene,
    Object,
    Mesh,
]
