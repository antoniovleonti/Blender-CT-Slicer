import bpy

# creates the slicing material
# this code is disgusting but better than doing it by hand, right? Right?!
def createShader():

    #make a new material
    if 'SLICES Material' in bpy.data.materials:
        #if it exists already, there's no need to make another one
        return bpy.data.materials["SLICES Material"]

    else:

        # Sorry for the lack of detailed comments here, I recommend looking at
        # the material if you want to know what this is doing or how it works
        # I honestly just did it by hand and copied the process to the script

        # if you know how to save materials to a file and load from that, send
        # me and email - aleonti@umassd.edu

        mat = bpy.data.materials.new(name="SLICES Material")
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        nodes.clear()

        # create nodes
        geometry = nodes.new(type="ShaderNodeNewGeometry")
        sepXYZ = nodes.new(type="ShaderNodeSeparateXYZ")
        lessThan = nodes.new(type="ShaderNodeMath")
        lessThan.operation = 'LESS_THAN'
        lessThan.inputs[1].default_value = .01
        greaterThan = nodes.new(type="ShaderNodeMath")
        greaterThan.operation = 'GREATER_THAN'
        greaterThan.inputs[1].default_value = 0
        cross = nodes.new(type="ShaderNodeMath")
        cross.operation = 'MULTIPLY'
        amp = nodes.new(type="ShaderNodeMath")
        amp.operation = 'MULTIPLY'
        amp.inputs[1].default_value = 100
        output = nodes.new(type="ShaderNodeOutputMaterial")

        # link nodes
        links.new(amp.outputs[0], output.inputs[1])
        links.new(geometry.outputs[0], sepXYZ.inputs[0])
        links.new(sepXYZ.outputs[2], lessThan.inputs[0])
        links.new(sepXYZ.outputs[2], greaterThan.inputs[0])
        links.new(greaterThan.outputs[0], cross.inputs[0])
        links.new(lessThan.outputs[0], cross.inputs[1])
        links.new(cross.outputs[0], amp.inputs[0])

        return mat

# allows you to find the max of model when rotated to qrot without permanently rotating it
def findZMax(model, qrot):

    model.select_set(True)                          #select model

    model.rotation_quaternion = qrot
    bpy.ops.object.transform_apply(rotation=True)   #apply rot

    zmax = model.dimensions[2]

    model.rotation_quaternion = [-x for x in qrot]   #rotate back
    model.rotation_quaternion[0] = 0
    bpy.ops.object.transform_apply(rotation=True)   #apply rot

    return zmax

# creates an animation for you - example qrot provided for convenience
# provided qrot looks at model from each axis place (xy, yz, xz)
def animate(model, qrot = [[1,1,0,0],[1,0,1,0],[1,0,0,1]], slicesPerAngle = 10):

    #clear keyframes
    model.animation_data_clear()
    #set interpolation ("tweener") type (DOESN'T WORK BUT NO ERROR?)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'

    #   precompute mesh limits for each angle
    zmax = [findZMax(model, x) for x in qrot]

    #finally, animate
    playhead = 0
    for i in range(len(qrot)):
        #   key
        model.rotation_quaternion = qrot[i]

        for j in range(2):

            playhead += 1 if j==0 else slicesPerAngle
            model.location = (0, 0, zmax[i]/2 if j==0 else -zmax[i]/2)

            model.keyframe_insert(data_path='location', frame=playhead)
            model.keyframe_insert(data_path='rotation_quaternion', frame=playhead)


    bpy.context.scene.frame_end = playhead
