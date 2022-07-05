import smplx
import torch
from pytorch3d.transforms import axis_angle_to_matrix
import numpy as np
import ipdb


class SmplMesh():

    def __init__(self, gender='male', device='cpu', batch_size=1, model_type='smpl', num_betas=10):
        model_folder = '/BS/garvita/work/SMPL_data/models'  #
        self.batch_size= batch_size
        body_model = smplx.build_layer(model_folder, model_type=model_type, gender=gender, num_betas=num_betas,
                                       batch_size=batch_size)  # we are running all the datasets for male gender
        self.body_model = body_model.to(device=device)

    def create_mesh(self, global_orient=None,pose=None,shape=None,trans=None,scale=1.0,):

        if shape is None:
            shape = np.zeros((10))
        global_orient = torch.from_numpy(global_orient).float().unsqueeze(0)
        pose = torch.from_numpy(pose).float().reshape(-1,3).unsqueeze(0)
        shape = torch.from_numpy(shape).float().unsqueeze(0)
        trans = torch.from_numpy(trans).float().unsqueeze(0)
        smpl_posed = self.body_model.forward(betas=shape, global_orient=axis_angle_to_matrix(global_orient), body_pose=axis_angle_to_matrix(pose))

        #apply scale
        return (smpl_posed['vertices'][0])*scale + trans[0], self.body_model.faces_tensor
