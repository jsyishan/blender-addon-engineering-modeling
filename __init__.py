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


if "bpy" in locals():
    import importlib
    importlib.reload(add_gear)
else:
    from . import add_gear

import bpy
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
