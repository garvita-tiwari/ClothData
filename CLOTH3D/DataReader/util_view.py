import bpy
import bmesh

PI = 3.14159

""" Scene """
def init(sample, info):
	# clean
	clean()
	# scene
	sc = scene(sample)
	# camera
	sc.camera = camera(info)
	# lights
	lights(info)
	
def clean():
	for ob in bpy.data.objects: 
		delete(ob)
		
def scene(sample):
	sc = bpy.data.scenes['Scene']
	sc.frame_current = 0
	
	sc.render.engine = 'BLENDER_EEVEE'
	sc.render.fps = 30
	sc.render.resolution_x = 640
	sc.render.resolution_y = 480
	sc.render.film_transparent = True

	return sc

def camera(info):
	bpy.ops.object.camera_add()
	ob = select('Camera')
	# Location
	ob.location = info['camLoc']
	# Orientation
	ob.rotation_euler[0] = PI / 2
	ob.rotation_euler[1] = 0
	ob.rotation_euler[2] = PI / 2
	
	return ob
	
def lights(info):
	type = info['lights']['type']
	data = info['lights']['data']
	if type == 'point':
		light_point(data)
	elif type == 'sun':
		light_sun(data)

def light_point(data):
	if type(data) is dict:
		bpy.ops.object.light_add()
		ob = bpy.context.object
		# Location	
		ob.location = data['loc']
		# Energy
		ob.data.energy = data['pwr']
	else:
		for light in data:
			bpy.ops.object.light_add()
			ob = bpy.context.object
			# Location	
			ob.location = light['loc']
			# Energy
			ob.data.energy = light['pwr']

def light_sun(data):
	bpy.ops.object.light_add()
	ob = bpy.context.object
	ob.data.type = 'SUN'
	# Direction
	ob.rotation_euler = data['rot']
	# Power
	ob.data.energy = data['pwr']
	# Ambient lighting
	world = bpy.data.worlds['World']
	world.use_nodes = True
	bg = world.node_tree.nodes['Background']
	bg.inputs[1].default_value = 1 + (data['pwr'] - 1.) / 9.

""" BPY obj manipulation """
def select(ob, only=True):
	if type(ob) is str: ob = bpy.data.objects[ob]
	if only: deselect()
	ob.select_set(True)
	bpy.context.view_layer.objects.active = ob
	return ob

def deselect():
	for obj in bpy.data.objects.values():
		obj.select_set(False)
	bpy.context.view_layer.objects.active = None
	
def delete(ob):
	select(ob)
	bpy.ops.object.delete()
	
def createBPYObj(V, F, Vt=None, Ft=None, name='new_obj'):
	# Create obj
	mesh = bpy.data.meshes.new('mesh')
	ob = bpy.data.objects.new(name, mesh)
	# Add to collection
	bpy.context.collection.objects.link(ob)
	select(ob)
	mesh = bpy.context.object.data
	bm = bmesh.new()
	# Vertices
	for v in V:
		bm.verts.new(v)
	bm.verts.ensure_lookup_table()
	# Faces
	for f in F:
		v = [bm.verts[i] for i in f]
		bm.faces.new(v)
	bm.to_mesh(mesh)
	bm.free()
	# UV Map
	if not Vt is None:
		# Create UV layer
		ob.data.uv_layers.new()
		# Assign UV coords
		iloop = 0
		for f in Ft:
			for i in f:
				ob.data.uv_layers['UVMap'].data[iloop].uv = Vt[i]
				iloop += 1				
	return ob
	
""" Modifiers """
def mesh_cache(ob, cache, scale=1):
	ob = select(ob)
	bpy.ops.object.modifier_add(type='MESH_CACHE')
	ob.modifiers['Mesh Cache'].cache_format = 'PC2'
	ob.modifiers['Mesh Cache'].filepath = cache
	ob.modifiers['Mesh Cache'].frame_scale = scale