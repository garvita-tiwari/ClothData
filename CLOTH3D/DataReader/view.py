import os
import sys
import bpy
import numpy as np

sys.path.append('.')
from IO import readOBJ, readPC2, writePC2, readPC2Frame
from util import loadInfo
from util_view import init, mesh_cache, createBPYObj

from smpl.smpl_np import SMPLModel

PATH_SRC = os.path.abspath(os.path.dirname(__file__)) + '/../Samples/'
PATH_CACHE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'view_cache')
PATH_SMPL = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'smpl')

# Init SMPL models
smpl = { 
	'f': SMPLModel(os.path.join(PATH_SMPL, 'model_f.pkl')),
	'm': SMPLModel(os.path.join(PATH_SMPL, 'model_m.pkl')),
}

def loadSMPL(sample, info):
	gender = 'm' if info['gender'] else 'f'
	# Create default SMPL object
	V, F = smpl[gender].verts, smpl[gender].faces
	ob = createBPYObj(V, F, Vt=None, Ft=None, name=sample)
	# Compute body sequence
	pc2_path = bodyCache(sample, info)
	# Assign mesh cache to SMPL object
	mesh_cache(ob, pc2_path)
	# z-rot
	ob.rotation_euler[2] = info['zrot']
	# Smooth
	bpy.ops.object.shade_smooth()

def bodyCache(sample, info):
	pc2_path = os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			'view_cache',
			sample + '.pc2'
		)
	if os.path.isfile(pc2_path): return pc2_path
	# Compute body sequence
	print("Computing body sequence...")
	print("")
	gender = 'm' if info['gender'] else 'f'
	N = info['poses'].shape[1]
	V = np.zeros((N, 6890, 3), np.float32)
	for i in range(N):
		sys.stdout.write('\r' + str(i+1) + '/' + str(N))
		sys.stdout.flush()
		p = info['poses'][:,i].reshape((24,3))
		s = info['shape']
		t = info['trans'][:,i].reshape((3,))
		v, j = smpl[gender].set_params(pose=p, beta=s, trans=t)
		V[i] = v - j[0:1]
	print("")
	print("Writing PC2 file...")
	writePC2(pc2_path, V)
	return pc2_path
	
def loadGarment(sample, garment, info):
	texture = info['outfit'][garment]['texture']
	# Read OBJ file and create BPY object
	V,F,Vt,Ft = readOBJ(os.path.join(PATH_SRC, sample, garment + '.obj'))
	ob = createBPYObj(V, F, Vt, Ft, name=sample + '_' + garment)
	# z-rot
	ob.rotation_euler[2] = info['zrot']
	# Convert cache PC16 to PC2
	pc2_path = garmentCache(sample, garment, info['trans'])
	mesh_cache(ob, pc2_path)
	# Set material
	setMaterial(ob, sample, garment, texture)
	# Smooth
	bpy.ops.object.shade_smooth()

def garmentCache(sample, garment, trans):
	pc2_path = os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			'view_cache',
			sample + '_' + garment + '.pc2'
		)
	if os.path.isfile(pc2_path): return pc2_path
	# Convert PC16 to PC2 (and move to view_cache folder)
	# Add trans to vertex locations
	pc16_path = os.path.join(PATH_SRC, sample, garment + '.pc16')
	V = readPC2(pc16_path, True)['V']
	for i in range(V.shape[0]):
		V[i] += trans[:,i][None]
	writePC2(pc2_path, V)
	return pc2_path
	
def setMaterial(ob, sample, garment, texture):
	mat = bpy.data.materials.new(name=sample + '_' + garment + '_Material')
	mat.use_nodes = True
	ob.data.materials.append(mat)
	if texture['type'] == 'color':
		mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = texture['data'].tolist() + [1]
	elif texture['type'] == 'pattern':
		# Read pattern
		img_path = os.path.join(PATH_SRC, sample, garment + '.png')
		# Add nodes
		tree = mat.node_tree
		nodes = tree.nodes
		# Principled BSDf
		bsdf = nodes['Principled BSDF']
		# Image
		img = nodes.new('ShaderNodeTexImage')
		img.image = bpy.data.images.load(img_path)
		# Links
		tree.links.new(img.outputs[0], bsdf.inputs[0])

def loadSampleSequence(sample, info):
	# Load SMPL
	loadSMPL(sample, info)
	
	# Load garments
	for garment in info['outfit']:
		loadGarment(sample, garment, info)
		
	bpy.context.scene.frame_end = info['poses'].shape[-1] - 1

def loadSampleFrame(sample, frame, info):
	""" SMPL """
	gender = 'm' if info['gender'] else 'f'
	p = info['poses'][:,frame].reshape((24,3))
	s = info['shape']
	t = info['trans'][:,frame]
	V, J = smpl[gender].set_params(pose=p, beta=s, trans=t)
	V -= J[0:1]
	ob = createBPYObj(V, smpl[gender].faces, name=sample)
	ob.rotation_euler[2] = info['zrot']		
	# Smooth
	bpy.ops.object.shade_smooth()
	# black object fix
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()
	""" Garments """
	for garment in info['outfit']:
		# Read OBJ file and create BPY object
		_,F,Vt,Ft = readOBJ(os.path.join(PATH_SRC, sample, garment + '.obj'))
		V = readPC2Frame(os.path.join(PATH_SRC, sample, garment + '.pc16'), frame, True)
		V += info['trans'][:,frame][None]
		ob = createBPYObj(V, F, Vt, Ft, name=sample + '_' + garment)
		# z-rot
		ob.rotation_euler[2] = info['zrot']		
		# Material
		setMaterial(ob, sample, garment, info['outfit'][garment]['texture'])	
		# Smooth
		bpy.ops.object.shade_smooth()
		# black object fix
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()
	
def viewSample(sample, frame=None):
	# Load sample info
	info_path = os.path.join(PATH_SRC, sample, 'info.mat')
	info = loadInfo(info_path)
	
	# Init scene
	init(sample, info)

	if frame is None: loadSampleSequence(sample, info)
	else: loadSampleFrame(sample, frame, info)

if __name__ == '__main__':
	try:
		# Parse args
		args = sys.argv
		while True:
			arg = args.pop(0)
			if arg == '--': break
		sample = args[0]
		frame = None
		if len(args) > 1:
			frame = int(args[1])
		# Check if sample exists
		if not os.path.isdir(os.path.join(PATH_SRC, sample)):
			print("Specified sample does not exist")
			sys.exit()
			
		viewSample(sample, frame)
	except:
		import traceback
		print('-'*60)
		print("SAMPLE: ", sample)
		print('-'*60)
		traceback.print_exc(file=sys.stdout)
		print('-'*60)
		sys.exit()