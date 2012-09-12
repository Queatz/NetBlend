import glm

class Object:
	_nb_type = 'object'
	def from_bl(self, bl, a):
		self.name = bl.name
		self.data = a(bl.data)
		self.parent = a(bl.parent)
		self.location = glm.vec3(*bl.location)
		self.rotation = glm.vec3(*bl.rotation_euler)
		self.scale = glm.vec3(*bl.scale)
		self.modifiers = [a(x) for x in bl.modifiers]
		self.constraints = [a(x) for x in bl.constraints]

class Mesh:
	_nb_type = 'mesh'
	def from_bl(self, bl, a):
		self.name = bl.name
		self.materials = [a(x) for x in bl.materials]
		self.vertices = [glm.vec3(*x.co) for x in bl.vertices]
		self.polygons = [
			[bl.loops[y].vertex_index for y in range(x.loop_start, x.loop_start + x.loop_total)]
			for x in bl.polygons]
