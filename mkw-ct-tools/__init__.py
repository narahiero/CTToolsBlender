
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
    importlib.reload(track_info)

else:
    from . import track_info


import bpy


classes = (
    track_info.SCENE_PG_mkwctt_race_settings,
    track_info.SCENE_PT_mkwctt_race_settings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mkwctt_race_settings = bpy.props.PointerProperty(type=track_info.SCENE_PG_mkwctt_race_settings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
