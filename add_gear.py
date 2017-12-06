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

def add_gear(m, z, h):

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
    bpy.context.screen.areas[4].spaces[0].cursor_location = (0.0, 0.0, 0.0)

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
    
    #enter edit mode
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    #remove doubles
    bpy.ops.mesh.remove_doubles()
    
    #init bmesh
    me = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    
    #select/unselect all vertices and edges
    #param Boolean@select to select(True) or unselect(False) all verts and edges
    #return None
    def handle_all_verts_and_edges(select):
        vertices = [e for e in bm.verts]
        edges = [e for e in bm.edges]

        for vert in vertices:
            vert.select = select
    
        for edge in edges:
            edge.select = select
    
    #set cursor to selected
    #param None
    #return None
    def set_cursor_to_selected():
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                ctx = bpy.context.copy()
                ctx['area'] = area
                ctx['region'] = area.regions[-1]
                bpy.ops.view3d.view_selected(ctx)
                bpy.ops.view3d.snap_cursor_to_selected(ctx)
                break
    
    #Duplicate involute
    bpy.ops.mesh.duplicate()
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
    
    #Connect the two top vertices of each involutes
    vertices = [e for e in bm.verts]
    
    if len(vertices) == 22:
        handle_all_verts_and_edges(False)
    
        vertices[10].select = True
        vertices[11].select = True
    
        bm.edges.new((vertices[10], vertices[11]))
    
    #Duplicate and rotate for a phi degree
    handle_all_verts_and_edges(True)

    bpy.ops.mesh.duplicate()
    
    selected_involute = list(filter(lambda v: v.select, bm.verts))
    
    center = bpy.context.scene.cursor_location
    rot = mathutils.Euler((0.0, 0.0, radians(phi))).to_matrix()
    
    bmesh.ops.rotate(
        bm,
        cent = center,
        matrix = rot,
        verts = selected_involute
    )
    
    #Draw a semi-circle between the two buttom vertices of the teeth
    handle_all_verts_and_edges(False)
    
    vertices = [e for e in bm.verts]
    vertices[21].select = True
    vertices[22].select = True
    
    set_cursor_to_selected()
    
    vertices[22].select = False
    
    bpy.ops.mesh.spin(
        steps = 16,
        dupli = False,
        angle = radians(180),
        center = bpy.context.screen.areas[4].spaces[0].cursor_location,
        axis = (0.0, 0.0, 1.0)
    )
    
    bpy.context.screen.areas[4].spaces[0].cursor_location = (0.0, 0.0, 0.0)
    
    #Duplicate and rotate until a full round
    handle_all_verts_and_edges(True)
    
    for i in range(z - 1):
        bpy.ops.mesh.duplicate()
        
        selected_involute = list(filter(lambda v: v.select, bm.verts))
    
        center = bpy.context.scene.cursor_location
        rot = mathutils.Euler((0.0, 0.0, radians(phi))).to_matrix()
    
        bmesh.ops.rotate(
            bm,
            cent = center,
            matrix = rot,
            verts = selected_involute
        )
    
    #Remove doubles
    handle_all_verts_and_edges(True)
    bpy.ops.mesh.remove_doubles()
    
    #Extrude
    if len(bm.verts) == 666:
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, h)})
    
    
    
    bmesh.update_edit_mesh(me, True)
    
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
