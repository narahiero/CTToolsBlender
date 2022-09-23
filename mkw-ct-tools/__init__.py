
bl_info = {
    "name": "MKW CT Tools",
    "description": "Tool aiming to allow full creation of CTs without leaving Blender",
    "author": "Nara Hiero",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "support": "COMMUNITY",
    "category": "MKW Modding",
}


if 'bpy' in locals():
    import importlib
    importlib.reload(utils)

else:
    from . import utils


import bpy


classes = (
    utils.devtools.MKWCTT_dev_settings,
    utils.devtools.MKWCTT_OT_reload_addon,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
