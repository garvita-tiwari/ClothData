import numpy as np
import scipy.io as sio
from math import cos, sin

def loadInfo(filename):
	'''
	this function should be called instead of direct sio.loadmat
	as it cures the problem of not properly recovering python dictionaries
	from mat files. It calls the function check keys to cure all entries
	which are still mat-objects
	'''
	data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
	del data['__globals__']
	del data['__header__']
	del data['__version__']
	return _check_keys(data)

def _check_keys(dict):
	'''
	checks if entries in dictionary are mat-objects. If yes
	todict is called to change them to nested dictionaries
	'''
	for key in dict:
		if isinstance(dict[key], sio.matlab.mio5_params.mat_struct):
			dict[key] = _todict(dict[key])
	return dict        

def _todict(matobj):
	'''
	A recursive function which constructs from matobjects nested dictionaries
	'''
	dict = {}
	for strg in matobj._fieldnames:
		elem = matobj.__dict__[strg]
		if isinstance(elem, sio.matlab.mio5_params.mat_struct):
			dict[strg] = _todict(elem)
		elif isinstance(elem, np.ndarray) and np.any([isinstance(item, sio.matlab.mio5_params.mat_struct) for item in elem]):
			dict[strg] = [None] * len(elem)
			for i,item in enumerate(elem):
				if isinstance(item, sio.matlab.mio5_params.mat_struct):
					dict[strg][i] = _todict(item)
				else:
					dict[strg][i] = item
		else:
			dict[strg] = elem
	return dict

# Computes matrix of rotation around z-axis for 'zrot' radians
def zRotMatrix(zrot):
	c, s = cos(zrot), sin(zrot)
	return np.array([[c, -s, 0],
					 [s,  c, 0],
					 [0,  0, 1]], np.float32)
""" CAMERA """
def intrinsic():
	RES_X = 640
	RES_Y = 480
	f_mm             = 50 # blender default
	sensor_w_mm      = 36 # blender default
	sensor_h_mm = sensor_w_mm * RES_Y / RES_X

	fx_px = f_mm * RES_X / sensor_w_mm;
	fy_px = f_mm * RES_Y / sensor_h_mm;

	u = RES_X / 2;
	v = RES_Y / 2;

	return np.array([[fx_px, 0,     u],
					 [0,     fy_px, v],
					 [0,     0,     1]], np.float32)
				
def extrinsic(camLoc):
	R_w2bc = np.array([[0, 1, 0],
					   [0, 0, 1],
					   [1, 0, 0]], np.float32)
	
	T_w2bc = -1 * R_w2bc.dot(camLoc)
	
	R_bc2cv = np.array([[1,  0,  0],
						[0, -1,  0],
						[0,  0, -1]], np.float32)
	
	R_w2cv = R_bc2cv.dot(R_w2bc)
	T_w2cv = R_bc2cv.dot(T_w2bc)

	return np.concatenate((R_w2cv, T_w2cv[:,None]), axis=1)
	
def proj(camLoc):
	return intrinsic().dot(extrinsic(camLoc))
	
""" 
Mesh to UV map
Computes correspondences between 3D mesh and UV map
NOTE: 3D mesh vertices can have multiple correspondences with UV vertices
"""
def mesh2UV(F, Ft):
	m2uv = {v: set() for f in F for v in f}
	for f, ft in zip(F, Ft):
		for v, vt in zip(f, ft):
			m2uv[v].add(vt)
	# m2uv = {k:list(v) for k,v in m2uv.items()}
	return m2uv
	
# Maps UV coordinates to texture space (pixel)
IMG_SIZE = 2048 # all image textures have this squared size
def uv_to_pixel(vt):
	px = vt * IMG_SIZE # scale to image plane
	px %= IMG_SIZE # wrap to [0, IMG_SIZE]
	# Note that Blender graphic engines invert vertical axis
	return int(px[0]), int(IMG_SIZE - px[1]) # texel X, texel Y