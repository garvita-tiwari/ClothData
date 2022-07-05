import os
# inp_file = '/BS/cloth3d/static00/Cloth3D/train/train/00001/Top.obj'
# target_file = '/BS/cloth3d/static00/Cloth3D/train/train/00001/Top_tri.obj'
# for o in bpy.data.objects:
#     bpy.ops.object.delete()
BLEND_FILE = '/BS/garvita2/work/vis_files/empty.blend'


def blend_edit(inp_file, target_file):
    import bpy
    print(inp_file)
    print(target_file)
    bpy.ops.import_scene.obj(filepath=inp_file)
    for obj in bpy.data.objects:


            bpy.context.scene.objects.active = obj
            # for vert in obj.vertices:
            #     vert.select = True
            bpy.ops.object.mode_set(mode='EDIT')
            # bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.mesh.quads_convert_to_tris()

            bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.export_scene.obj(filepath=target_file)


def edit_func(inp_file, target_file):
    thispath = os.path.abspath(__file__)
    cmd = "blender --background {} -P {}  -- --inp_file {} --target_file {} ".format(
        BLEND_FILE,
        thispath,
        inp_file,
        target_file,

    )
    os.system(cmd)


if __name__ == "__main__":
    import sys
    sys.argv = [sys.argv[0]] + sys.argv[6:]
    print(sys.argv)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--inp_file')
    parser.add_argument('--target_file')
    args = parser.parse_args()
    print(args)

    blend_edit(args.inp_file, args.target_file)