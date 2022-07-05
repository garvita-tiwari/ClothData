import os
import ipdb
from quad2tri_blender import edit_func
if __name__ == "__main__":

    source_dir = '/BS/cloth3d/static00/Cloth3D'
    for split in ['train']:
        split_dir = source_dir + '/{}/{}'.format(split, split)
        all_samples = sorted(os.listdir(split_dir))
        for sample in all_samples:
            data_dir = os.path.join(split_dir, sample)
            all_files = os.listdir(data_dir)
            for file_name in all_files:
                if not '.obj' in file_name or 'tri' in file_name:
                    continue
                out_path = os.path.join(data_dir, file_name[:-4] + '_tri.obj')
                if os.path.exists(out_path):
                    print('already done', file_name)
                else:
                    edit_func(os.path.join(data_dir, file_name), out_path)
                    print(' done', file_name)
                # ipdb.set_trace()

