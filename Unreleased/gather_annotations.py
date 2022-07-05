"""Temp file to gather annotations for scans into a directory"""
"""Temp file to gather scan and scan tex for scans into a directory"""

import os
import shutil
import sys
import ipdb

if __name__ == "__main__":
    out_dir = '/BS/cloth3d/static00/internal/twindom_new_10k'
    in_dir = '/BS/garvita2/static00/twindom_new_10k'
    out_dir = '/BS/cloth3d/static00/internal/treddy'
    in_dir = '/BS/bahar/work/Annotations/original2'
    in_dir = '/BS/garvita/work/registration_data/registration_results/treddy'

    in_dir = '/BS/RVH/work/data/twindom_new_10k/original'
    out_dir = '/BS/cloth3d/static00/internal/twindom_new_10k'

    in_dir = '/BS/bharat-2/static00/renderings/renderpeople_rigged'
    out_dir = '/BS/cloth3d/static00/internal/renderpeople_rigged'
    ann_done = []
    all_scans = sorted(os.listdir(in_dir))
    for scan in all_scans:
        # if not '.obj' in scan:
        #     continue
        # scan = scan[:-4]
        scan = scan
        out_f = os.path.join(out_dir,scan)
        if not os.path.exists(out_f):
            os.makedirs(out_f)

        #
        # obj_file = os.path.join(in_dir, scan+'.obj')
        # tex_file = os.path.join(in_dir, scan+'.jpg')
        # mtl_file = os.path.join(in_dir, scan+'.mtl')
        #
        # obj_file_out = os.path.join(out_dir, scan, scan+'.obj')
        # tex_file_out = os.path.join(out_dir,  scan, scan+'.jpg')
        # mtl_file_out = os.path.join(out_dir, scan,  scan+'.mtl')

        obj_file = os.path.join(in_dir, scan, scan+'.obj')
        tex_file = os.path.join(in_dir, scan, scan+'_orig.jpg')
        # mtl_file = os.path.join(in_dir, scan+'.mtl')

        obj_file_out = os.path.join(out_dir, scan, scan+'.obj')
        tex_file_out = os.path.join(out_dir,  scan, scan+'.jpg')
        # mtl_file_out = os.path.join(out_dir, scan,  scan+'.mtl')

        ann_file = os.path.join(in_dir, scan, '{}_annotations.json'.format(scan))
        ann_file_out = os.path.join(out_dir, scan, '{}_annotations.json'.format(scan))
        # print(tex_file)
        if os.path.exists(obj_file):
            shutil.copyfile(obj_file, obj_file_out)
            shutil.copyfile(tex_file, tex_file_out)
            # shutil.copyfile(mtl_file, mtl_file_out)
            # shutil.copyfile(ann_file, ann_file_out)
            #
            # if os.path.exists(ann_file_out):
            #     print('annotation exists')
            #     ann_done.append(scan)
            # else:
            #     shutil.copyfile(ann_file, ann_file_out)
            print('done...', scan)
    ipdb.set_trace()