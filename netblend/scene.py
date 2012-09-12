import glm

class Scene:
	_nb_type = 'scene'
	def from_bl(self, bl, a):
		self.name = bl.name
		self.world = a(bl.world)
		self.camera = a(bl.camera)
		self.objects = [a(x) for x in bl.objects]

class WorldMist:
	_nb_type = 'worldmist'
	def from_bl(self, bl, a):
		self.falloff = {
			'LINEAR': 'linear',
			'QUADRATIC': 'quadratic',
			'INVERSE_QUADRATIC': 'inverse quadratic',
		}[bl.falloff]
		self.depth = bl.depth
		self.start = bl.start
		self.constant = bl.intensity

class World:
	_nb_type = 'world'
	def from_bl(self, bl, a):
		if bl.mist_settings.use_mist:
			self.mist = a(bl.mist_settings)
			
		self.ambient = glm.vec3(
			bl.ambient_color.r,
			bl.ambient_color.g,
			bl.ambient_color.b,
		)
		self.horizon = glm.vec3(
			bl.horizon_color.r,
			bl.horizon_color.g,
			bl.horizon_color.b,
		)
		self.zenith = glm.vec3(
			bl.zenith_color.r,
			bl.zenith_color.g,
			bl.zenith_color.b,
		)
