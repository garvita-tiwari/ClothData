import os
import sys
import numpy as np
from PIL import Image

from smpl.smpl_np import SMPLModel
from util import loadInfo, zRotMatrix, proj, mesh2UV, uv_to_pixel
from IO import readOBJ, readPC2Frame

class DataReader:

	def __init__(self):
		# Data paths
		self.SRC = os.path.abspath(os.path.dirname(__file__)) + '/../Samples/'
		# SMPL model
		smpl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'smpl')
		self.smpl = {
			'f': SMPLModel(os.path.join(smpl_path, 'model_f.pkl')),
			'm': SMPLModel(os.path.join(smpl_path, 'model_m.pkl'))
		}
		
	""" 
	Read sample info 
	Input:
	- sample: name of the sample e.g.:'01_01_s0'
	"""
	def read_info(self, sample):
		info_path = os.path.join(self.SRC, sample, 'info')
		return loadInfo(info_path)
		
	""" Human data """
	"""
	Read SMPL parameters for the specified sample and frame
	Inputs:
	- sample: name of the sample
	- frame: frame number
	"""
	def read_smpl_params(self, sample, frame):
		# Read sample data
		info = self.read_info(sample)
		# SMPL parameters
		gender = 'm' if info['gender'] else 'f'
		if len(info['poses'].shape) == 1: frame = None
		pose = info['poses'][:, frame].reshape(self.smpl[gender].pose_shape)
		shape = info['shape']
		trans = info['trans'][:, frame].reshape(self.smpl[gender].trans_shape)
		return gender, pose, shape, trans
	
	"""
	Computes human mesh for the specified sample and frame
	Inputs:
	- sample: name of the sample
	- frame: frame number
	- absolute: True for absolute vertex locations, False for locations relative to SMPL root joint	
	Outputs:
	- V: human mesh vertices
	- F: mesh faces
	"""
	def read_human(self, sample, frame, absolute=True):
		# Read sample data
		info = self.read_info(sample)
		# SMPL parameters
		gender, pose, shape, trans = self.read_smpl_params(sample, frame)
		# Compute SMPL
		V, J = self.smpl[gender].set_params(pose=pose, beta=shape, trans=trans if absolute else None)
		V -= J[0:1]
		# Apply rotation on z-axis
		zRot = zRotMatrix(info['zrot'])
		return zRot.dot(V.T).T, self.smpl[gender].faces
	
	""" Garment data """
	"""
	Reads garment vertices location for the specified sample, garment and frame
	Inputs:
	- sample: name of the sample
	- garment: type of garment (e.g.: 'Tshirt', 'Jumpsuit', ...)
	- frame: frame number
	- absolute: True for absolute vertex locations, False for locations relative to SMPL root joint	
	Outputs:
	- V: 3D vertex locations for the specified sample, garment and frame
	"""
	def read_garment_vertices(self, sample, garment, frame, absolute=True):
		# Read garment vertices (relative to root joint)
		pc16_path = os.path.join(self.SRC, sample, garment + '.pc16')
		V = readPC2Frame(pc16_path, frame, True)
		# Read sample data
		info = self.read_info(sample)		
		if absolute:
			# Transform to absolute
			if len(info['trans'].shape) == 1: frame = None
			V += info['trans'][:,frame].reshape((1,3))
		# Apply rotation on z-axis
		zRot = zRotMatrix(info['zrot'])
		return zRot.dot(V.T).T

	"""
	Reads garment faces for the specified sample and garment
	Inputs:
	- sample: name of the sample
	- garment: type of garment (e.g.: 'Tshirt', 'Jumpsuit', ...)
	Outputs:
	- F: mesh faces	
	"""
	def read_garment_topology(self, sample, garment):
		# Read OBJ file
		obj_path = os.path.join(self.SRC, sample, garment + '.obj')
		return readOBJ(obj_path)[1]

	"""	
	Reads garment UV map for the specified sample and garment
	Inputs:
	- sample: name of the sample
	- garment: type of garment (e.g.: 'Tshirt', 'Jumpsuit', ...)
	Outputs:
	- Vt: UV map vertices
	- Ft: UV map faces		
	"""
	def read_garment_UVMap(self, sample, garment):
		# Read OBJ file
		obj_path = os.path.join(self.SRC, sample, garment + '.obj')
		return readOBJ(obj_path)[2:]		

	"""
	Reads vertex colors of the specified sample and garment
	Inputs:
	- sample: name of the sample
	- garment: type of garment (e.g.: 'Tshirt', 'Jumpsuit', ...)
	- F: mesh faces
	- Vt: UV map vertices
	- Ft: UV map faces
	Output
	- C: RGB colors
	"""
	def read_garment_vertex_colors(self, sample, garment, F, Vt, Ft):
		# Read sample texture info
		texture = self.read_info(sample)['outfit'][garment]['texture']
		# Plain color
		if texture['type'] == 'color': return (255*texture['data']).astype(np.int32)
		# Image texture
		img_path = os.path.join(self.SRC, sample, garment + '.png')
		img = Image.open(img_path)
		# Get color of each UV vertex
		color = np.array([img.getpixel(uv_to_pixel(vt)) for vt in Vt])
		# Compute correspondece between V (mesh) and Vt (UV map)
		m2uv = mesh2UV(F, Ft)
		return np.array([color[list(m2uv[idx])].mean(0) for idx in sorted(list(m2uv.keys()))], np.uint8)
		
	""" Scene data """
	"""
	Read camera location and compute projection matrix
	Input:
	- sample: name of the sample
	Output:
	- P: camera projection matrix (3 x 4)
	"""
	def read_camera(self, sample):
		# Read sample data
		info = self.read_info(sample)
		# Camera location
		camLoc = info['camLoc']
		# Camera projection matrix
		return proj(camLoc)
		
# TESTING
if __name__ == '__main__':
	sample = '135_02_s8'
	frame = 0
	garment = 'Tshirt'
	
	reader = DataReader()
	F = reader.read_garment_topology(sample, garment)
	Vt, Ft = reader.read_garment_UVMap(sample, garment)
	C = reader.read_garment_vertex_colors(sample, garment, F, Vt, Ft)