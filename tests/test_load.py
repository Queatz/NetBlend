# This script needs scge installed.
# See: http://github.com/Queatz/Simple-C---Game_Engine/
import scge
import glm
import scge.shared.debug as debug

import netblend
import netblend.standard

class Window:
	def __init__(self, *args):
		scge.window(*args)
		scge.vsync()
	
	def setup(self):
		self.nb = netblend.open(netblend.standard.defs, 'NetBlendAddon.netblend')
		
		self.obj = None
		for o in self.nb.walk():
			if isinstance(o, netblend.standard.Mesh):
				self.obj = o
				break
		
	def loop(self):
		self.setup()
		while scge.window_opened() and not scge.key('escape'):
			scge.poll()
			
			if self.obj:
				scge.clear()
			
				debug.begin()
				debug.matrix(glm.ortho(-2, 2, -2, 2, -2, 2))
				for v in self.obj.vertices:
					debug.point(v.x, v.y)
				debug.end()
			
			scge.swap()

w = Window('NetBlend Loading Test', 640, 640)
w.loop()
