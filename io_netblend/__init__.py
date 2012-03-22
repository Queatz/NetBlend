import sys, os.path
sys.path.append(os.path.dirname(__file__))

import netblend
import netblend.standard

import bpy

# NetBlend Types #

class NetBlendTypes:
    class Skeleton:
        def __init__(self, props, match):
            self.props = props
            self.matches = match
            self.blender_objects = {}
            self.netblend = netblend.NetBlend()
        
        def get(self, bo):
            if not bo:
                return None
            
            bot = bo.bl_rna.identifier
            
            boi = bot + bo.name
            
            if boi in self.blender_objects:
                return self.blender_objects[boi]
            
            if bot not in self.matches:
                return None
            
            a = self.matches[bot]()
            a.skeleton = self
            self.blender_objects[boi] = a
            a.make(bo)
            
            self.netblend.add(a.nb)
            
            if self.props.export in ('ALL', 'SCENE'):
                a.walk(bo)
            
            return a
        
        add = get
            
    
    class Converter:
        #skeleton = None
        def make(self, bo):
            print('Exporting of ' + self.__class__.__name__ + ' is not implemented.')
        
        def salvage(self, nb):
            print('Importing of ' + self.__class__.__name__ + ' is not implemented.')
        
        def walk(self, bo):
            pass
    
    class Scene(Converter):
        def make(self, bo):
            self.nb = netblend.standard.Scene()
            nb = self.nb
            
            nb.name = netblend.standard.String(bo.name)
            a = self.skeleton.get(bo.camera)
            if a:
	            nb.camera = a.nb
        
        def walk(self, bo):
            # Add objects from scene
            for o in bo.objects:
                a = self.skeleton.add(o)
                
                if a:
                    self.nb.objects.append(a.nb)
    
    class Object(Converter):
        def make(self, bo):
            self.nb = netblend.standard.Object()
            nb = self.nb
            
            nb.name = netblend.standard.String(bo.name)
            
            a = self.skeleton.get(bo.data)
            nb.data = (None if not a else a.nb)
            
            if self.skeleton.props.export in ('ALL', 'SCENE') or self.skeleton.props.export == 'SELECTION' and bo.parent and bo.parent.select:
                a = self.skeleton.get(bo.parent)
                nb.parent = (None if not a else a.nb)
            
            nb.location.x = bo.location.x
            nb.location.y = bo.location.y
            nb.location.z = bo.location.z
            
            nb.rotation.x = bo.rotation_euler.x
            nb.rotation.y = bo.rotation_euler.y
            nb.rotation.z = bo.rotation_euler.z
            
            nb.scale.x = bo.scale.x
            nb.scale.y = bo.scale.y
            nb.scale.z = bo.scale.z
        
        def walk(self, bo):
            # Add children of object
            for o in bo.children:
                self.skeleton.add(o)
    
    class Mesh(Converter):
        def make(self, bo):
            self.nb = netblend.standard.Mesh()
            
            self.nb.name = netblend.standard.String(bo.name)
            
            for v in bo.vertices:
                self.nb.vertices.append(
                    netblend.standard.Vec3(*v.co)
                )
            
            for f in bo.faces:
                self.nb.faces.append(
                    [self.nb.vertices[x] for x in f.vertices]
                )
        
    
    
    

# NetBlend Write #

netblend_btypes = {}
for x in dir(NetBlendTypes):
    a = getattr(NetBlendTypes, x)
    try:
        if issubclass(a, NetBlendTypes.Converter):
            netblend_btypes[x] = a
    except:
        pass

def write_netblend(context, filepath, props):
    print('Exporting NetBlend...')
    
    ##if props.use_low_precision:
    #    netblend.standard.options.vec3 = netblend.standard.Vec3_lowp
    #else:
    #    netblend.standard.options.vec3 = netblend.standard.Vec3
    
    skele = NetBlendTypes.Skeleton(props, netblend_btypes)
    if props.export == 'ALL':
        if len(bpy.data.scenes) < 1:
            print('Cancelling: No scenes.')
            return {'CANCELLED'}
        for scene in bpy.data.scenes:
            skele.add(scene)
    
    elif props.export == 'SCENE' or len(bpy.context.scene.objects) < 1:
        if not bpy.context.scene:
            print('Cancelling: No objects.')
            return {'CANCELLED'}
        
        for o in bpy.context.scene.objects:
            skele.add(o)
    
    elif props.export == 'SELECTION':
        if len(bpy.context.selected_objects) < 1:
            print('Cancelling: No selection.')
            return {'CANCELLED'}
        for object in bpy.context.selected_objects:
            skele.add(object)
    
    elif props.export == 'DATA':
        if not bpy.context.object or not bpy.context.object.data:
            print('Cancelling: No data.')
            return {'CANCELLED'}
        skele.add(bpy.context.object.data)
    
    f = open(filepath, 'wb+')
    skele.netblend.write(netblend.standard.defs, f)
    f.close()

    return {'FINISHED'}

# NetBlend Addon #

bl_info = {
    'name': 'NetBlend',
    'author': 'Jacob Ferrero',
    'version': (0, 0, 1),
    'blender': (2, 6, 3),
    'location': 'File > Export > NetBlend',
    'warning': 'Incomplete',
    'description': 'A compact and minimal blend format.',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts',
    'tracker_url': 'http://projects.blender.org/tracker/',
    'category': 'Import-Export'}

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


class ExportNetBlend(bpy.types.Operator, ExportHelper):
    '''A compact and minimal blender format.'''
    bl_idname = 'export.netblend'  # this is important since its how bpy.ops.export.netblend is constructed
    bl_label = 'Export NetBlend'

    # ExportHelper mixin class uses this
    filename_ext = '.netblend'

    filter_glob = StringProperty(
            default='*.netblend',
            options={'HIDDEN'}
            )

    export = EnumProperty(
        name = 'Export',
        description = 'What to export.',
        items=(
            ('ALL', 'All Scenes', 'Export everything.'),
            ('SCENE', 'Current Scene', 'Export only the active scene.'),
            ('SELECTION', 'Selected Objects', 'Export only the selected objects.'),
            ('DATA', 'Active Data', 'Export only the data from the active object.'),
        ),
        default='ALL',
    )

    use_low_precision = BoolProperty(
            name = 'Low Precision',
            description = 'Use low precision in exchange for a smaller file.',
            default = False,
        )

    use_include_names = BoolProperty(
            name = 'Names',
            description = 'Include object and data names in the export.',
            default = True,
        )

    use_include_uv_textures = BoolProperty(
            name = 'UV Textures',
            description = 'Include uv textures in the export.',
            default = True,
        )

    use_include_vertex_colors = BoolProperty(
            name = 'Vertex Colors',
            description = 'Include vertex colors in the export.',
            default = True,
        )

    use_include_modifiers = BoolProperty(
            name = 'Modifiers',
            description = 'Include modifiers in the export.',
            default = True,
        )

    use_include_constraints = BoolProperty(
            name = 'Constraints',
            description = 'Include constraints in the export.',
            default = True,
        )

    use_include_materials = BoolProperty(
            name = 'Materials',
            description = 'Include materials in the export.',
            default = True,
        )

    def execute(self, context):
        return write_netblend(context, self.filepath, self)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportNetBlend.bl_idname, text = 'NetBlend (.netblend)')


def register():
    bpy.utils.register_class(ExportNetBlend)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportNetBlend)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()

    # test call
    bpy.ops.export.netblend('INVOKE_DEFAULT')
