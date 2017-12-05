import bpy

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

    psi = 360 * (pi / 2 + z * (tan(radians(20) - radians(20)))) / (pi * z)  #Tooth thickness at base(radians)

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

bl_info= {
    "name": "engineering_modeling_tools",
    "author": "V.Eugen",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add Engineering object types",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh"
    }


from . import add_gear

from bpy.types import Menu


class INFO_MT_mesh_gears_add(Menu):
    bl_idname = "INFO_MT_mesh_gears_add"
    bl_label = "Gears"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.involute_gear", text="Involute Gear")

class INFO_MT_mesh_engineering_modeling(Menu):
    bl_idname = "INFO_MT_mesh_em_add"
    bl_label = "Engineering Modeling"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.menu("INFO_MT_mesh_gears_add", text="Gears", icon="SCRIPTWIN")


def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'

    layout.separator()
    layout.menu(
        "INFO_MT_mesh_em_add",
        text="Engineering Modeling",
        icon="SCRIPTWIN")

        
def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
