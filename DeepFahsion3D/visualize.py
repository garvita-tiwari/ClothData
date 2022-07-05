"""Visualise clothing mesh with body underneath"""
import sys
sys.path.append('/BS/garvita/work/code/ClothData')
from utils.create_smpl import SmplMesh


import os
import pickle as pkl
import ipdb
from pytorch3d.io import load_objs_as_meshes, save_obj

DATA_DIR = '/BS/cloth3d/static00/DeepFashion3D'

if __name__ == "__main__":
    cloth_dir = os.path.join(DATA_DIR, 'deep_fashion_3d_point_cloud')
    pose_dir = os.path.join(DATA_DIR, 'df3d_pose_to_release/packed_pose')
    body_dir = os.path.join(DATA_DIR, 'df3d_pose_to_release/smpl_mesh')

    cloth_ids = range(600)
    pose_ids = range(18)
    smpl_mesh= SmplMesh()
    for cloth_id in cloth_ids:
        for pose_id in pose_ids:
            cloth_mesh = os.path.join(cloth_dir, '{}-{}.ply'.format(cloth_id, pose_id))
            pose_file = os.path.join(pose_dir,  '{}/{}-{}.pkl'.format(cloth_id, cloth_id, pose_id))
            body_path =  os.path.join(body_dir, '{}-{}.obj'.format(cloth_id, pose_id))
            if os.path.exists(cloth_mesh) and os.path.exists(pose_file):
                #create smpl mesh

                smpl_data = pkl.load(open(pose_file, 'rb'))
                body_verts, body_faces = smpl_mesh.create_mesh(global_orient=smpl_data['pose'][:3], pose=smpl_data['pose'][3:],trans=smpl_data['trans'], scale=smpl_data['scale'])
                save_obj(body_path, body_verts,body_faces)
                ipdb.set_trace()

            else:
                print('missings file:  {}-{}'.format(cloth_id, pose_id) )