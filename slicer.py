import bpy
import math
import time

# TODO:
# 1. import
# 2. rendering, export path change


#USER PARAMETERS

#of slices per rotation
SLICES_PER_ANGLE = 100
#list of orientations to slice model in
QUATERNION_ROTATION = [[1,1,0,0],[1,0,1,0],[1,0,0,1]]

def main():
    
    scene = bpy.context.scene
    
    scene.render.image_settings.file_format = 'TIFF'
    scene.render.image_settings.color_mode = 'BW'
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 16
    


    #   grab & "prep" model
    
    model = bpy.data.objects['SLICES Model']
    model.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    model.rotation_mode = 'QUATERNION'
    
    #take care of origin
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
    
    #   scale model so largest dimension is 10m
    
    max = 0
    for i in range(3):
        #find largest dimension
        if model.dimensions[i] > model.dimensions[max]:
            max = i;
    #find appropriate scale
    scale = 2/model.dimensions[max]

    #scale each dimension
    for i in range(3):
        model.scale[i] = scale
        
    model.select_set(True) #select model
    bpy.ops.object.transform_apply(scale=True) #apply scale
        
    
    #   create and apply "slice" material to model
    
    mat = createBoolean()
    #safety check
    if model.data.materials:
        model.data.materials[0] = mat
    else:
        model.data.materials.append(mat)
        
        
    #   animate object through xy plane
    
    animate(model, QUATERNION_ROTATION, SLICES_PER_ANGLE)
    
    if not 'SLICES Camera' in bpy.data.objects:
    
        # create camera data
        camdata = bpy.data.cameras.new("SLICES Camera")
        camdata.type = 'ORTHO'
        camdata.ortho_scale = 3

        # create camera object
        camera = bpy.data.objects.new("SLICES Camera", camdata)
        camera.location = (0, 0, 3)
        camera.rotation_euler = (0, 0, 0)
        
        scene.collection.objects.link(camera)
        
        
        
def createBoolean():
    #make a new material
    if 'SLICES Material' in bpy.data.materials:
        #if it exists already, there's no need to make another one
        return bpy.data.materials['SLICES Material']
    
    else:
        
        mat = bpy.data.materials.new(name="SLICES Material")
        mat.use_nodes = True
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        nodes.clear()

        #   create nodes
        
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
        
        #   link nodes
        
        links.new(amp.outputs[0], output.inputs[1])
        links.new(geometry.outputs[0], sepXYZ.inputs[0])
        links.new(sepXYZ.outputs[2], lessThan.inputs[0])
        links.new(sepXYZ.outputs[2], greaterThan.inputs[0])
        links.new(greaterThan.outputs[0], cross.inputs[0])
        links.new(lessThan.outputs[0], cross.inputs[1])
        links.new(cross.outputs[0], amp.inputs[0])
    
        return mat



def findZMax(model, qrot):
    
    model.select_set(True)                          #select model
        
    model.rotation_quaternion = qrot
    bpy.ops.object.transform_apply(rotation=True)   #apply rot
        
    zmax = model.dimensions[2]

    model.rotation_quaternion = [-x for x in qrot]   #rotate back
    model.rotation_quaternion[0] = 0
    bpy.ops.object.transform_apply(rotation=True)   #apply rot
    
    return zmax



def animate(model, qrot, slicesPerAngle = 10):
    
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



if __name__ == "__main__":
    main()
