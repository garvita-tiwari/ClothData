import os
import numpy as np
from IO import readPC2, writePC2, readFaceBIN, writeFaceBIN

"""
Compresses vertices and mesh topology into binary files.
Preemptively performs a sanity check on the inputs:
Inputs:
- fname: path to files to be created, NO extension, as it shall be automatically assigned
- V: animation data (vertex locations), must be a TxNx3 NumPy array, where T = N. frames and N = N. vertices
- F: mesh faces as triangles, must be a Nx3 NumPy array, where N = N. faces
"""
def compress(fname, V, F):
	# Sanity check for fname
	assert '.' not in os.path.basename(fname), "File name should not have an extension (it will be assigned by this function)"
	# Sanity check for vertices
	assert type(V) == np.ndarray, "Vertices must be an TxNx3 NumPy array"
	assert len(V.shape) == 3 and V.shape[2] == 3, "Vertices have the wrong shape (should be TxNx3)"
	# Sanity check for faces
	assert type(F) == np.ndarray, "Faces must be an Nx3 NumPy array"
	assert len(F.shape) == 2 and F.shape[1] == 3, "Faces have the wrong shape (should be Nx3)"
	# Writing
	writePC2(fname + '.pc16', V, float16=True)
	writeFaceBIN(fname + '.bin', F)

"""
Decompresses files written in the submission format (compressed binaries).
Input:
- fname: path to where files are, NO extension must be provided, it shall be automatically assigned
Outputs:
- V: animation data (vertex locations), it is a TxNx3 NumPy array, where T = N. frames and N = N. vertices
- F: mesh faces as triangles, it is a Nx3 NumPy array, where N = N. faces

"""
def decompress(fname):
	# Sanity check for fname
	assert '.' not in os.path.basename(fname), "File name should not have an extension (it will be assigned by this function)"
	# Read vertices
	V = readPC2(fname + '.pc16', float16=True)['V']
	# Read faces
	F = readFaceBIN(fname + '.bin')
	return V, F