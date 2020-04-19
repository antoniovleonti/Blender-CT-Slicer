import bpy
import slice

# TODO: (This code isn't useful to me anymore - I'll probably never implement these unfortunately)
# 1. import
# 2. rendering, export path change


#USER PARAMETERS

def main():
    # CYCLES renderer is needed for the slicing material to work
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'

    # grab model
    model = bpy.data.objects["SLICES Model"]
    model.select_set(True)

    # apply any pending transformations to model
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # I need quaternion rotations
    model.rotation_mode = "QUATERNION"
    #make sure origin is right
    bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="MEDIAN")

    # scale object so that largest dim is 1m
    scale = 1 / max(model.dimensions)           # find appropriate scale
    model.scale = (scale,)*3                    # apply scale to each dimension
    model.select_set(True)                      # select model
    bpy.ops.object.transform_apply(scale=True)  # apply scale


    # create and apply "slice" material to model
    mat = slice.createShader()
    model.data.materials.append(mat)

    # animate object through xy plane

    slice.animate(model)

    if not "SLICES Camera" in bpy.data.objects:

        # create camera data
        camdata = bpy.data.cameras.new("SLICES Camera")
        camdata.type = "ORTHO"
        camdata.ortho_scale = 3

        # create camera object
        camera = bpy.data.objects.new("SLICES Camera", camdata)
        camera.location = (0, 0, 1.5)
        camera.rotation_euler = (0, 0, 0)

        scene.collection.objects.link(camera)

if __name__ == "__main__":
    main()
