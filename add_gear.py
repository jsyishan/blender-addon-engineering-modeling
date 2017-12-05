import bpy
import bmesh

import mathutils
from bpy.types import Operator
from math import (
    sin, cos, tan, 
    sqrt, 
    pi, 
    radians
    )

from bpy.props import (
    FloatProperty, IntProperty
    )

def add_gear(m, z):

    if z < 2:
        return False
    
    r = m * z * cos(radians(20)) / 2    #Base Radius
    R = m * (z / 2.0 + 1)   #Tip Radius

    psi = 360 * (pi / 2 + z * (tan(radians(20)) - radians(20))) / (pi * z)  #Tooth thickness at base(angles)

    phi = 360.0 / z

    invx = str(round(r, 4)) + " * (cos(u) + u * sin(u))";   #X-equation
    invy = str(round(r, 4)) + " * (sin(u) - u * cos(u))";   #Y-equation
    invz = "0"  #Z-equation

    umin = 0.0
    umax = sqrt((R * R) / (r * r) - 1)
    ustep = 10.0
    uwrap = False

    vmin = 0.0
    vmax = 0.0
    vstep = 1.0

    #set pivot point type and location
    
    bpy.context.screen.areas[4].spaces[0].pivot_point = 'CURSOR'
    # bpy.context.area.spaces[0].cursor_location = (0.0, 0.0, 0.0)

    #draw involute
    bpy.ops.mesh.primitive_xyz_function_surface(
        x_eq = invx,
        y_eq = invy,
        z_eq = invz,
        range_u_min = umin,
        range_u_max = umax,
        range_u_step = ustep,
        wrap_u = uwrap,
        range_v_min = vmin,
        range_v_max = vmax,
        range_v_step = vstep
    )
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.remove_doubles()
    
    mesh = bpy.context.active_object.data
    first_involute = list(filter(lambda v: v.select, mesh.vertices))
    
    #Duplicate involute
    bpy.ops.mesh.duplicate()
    
    me = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    selected_involute = list(filter(lambda v: v.select, bm.verts))
    
    #Scale the selected involute
    scale = mathutils.Vector((1.0, -1.0, 1.0))
    bmesh.ops.scale(
        bm,
        vec = scale,
        verts = selected_involute
        )
        
    #Rotate the selected involute
    center = bpy.context.scene.cursor_location
    rot = mathutils.Euler((0.0, 0.0, radians(psi))).to_matrix()
    
    bmesh.ops.rotate(
        bm,
        cent = center,
        matrix = rot,
        verts = selected_involute
    )
    
    bmesh.update_edit_mesh(me, True)
    
    #second_involute.scale(1.0, -1.0, 1.0)
    #second_involute.rotation_euler = (0.0, 0.0, psi)
    
    return True

class AddGear(Operator):
    bl_idname = "mesh.involute_gear"
    bl_label = "Add Involute Gear"
    bl_description = "Create an involute gear"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    m = FloatProperty(
        name = "Module of Gear",
        description = "Module of the gear",
        min = 0.1,
        max = 100.0,
        default = 1.0,
        unit = 'LENGTH'
    )
    
    z = IntProperty(
        name = "Number of Teeth",
        description = "Number of Teeth on the gear",
        min = 2,
        max = 256,
        default = 18
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'm')
        box.prop(self, 'z')

    def execute(self, context):
        flag = add_gear(self.m, self.z)

        if flag:
            return {'FINISHED'}

        return {'CANCELLED'}
