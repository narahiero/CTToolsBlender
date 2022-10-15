
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
    importlib.reload(collection_settings)
    importlib.reload(collision_settings)
    importlib.reload(export)
    importlib.reload(export_info)
    importlib.reload(model_settings)
    importlib.reload(track_info)
    importlib.reload(utils)

else:
    from . import collection_settings
    from . import collision_settings
    from . import export
    from . import export_info
    from . import model_settings
    from . import track_info
    from . import utils


import bpy


classes = (
    export_info.SCENE_PG_mkwctt_export_info,
    export_info.SCENE_OT_mkwctt_export,
    export_info.SCENE_PT_mkwctt_export_info,

    track_info.SCENE_PG_mkwctt_race_settings,
    track_info.SCENE_PT_mkwctt_race_settings,

    collection_settings.COLLECTION_PG_mkwctt_collection_settings,
    collection_settings.COLLECTION_PT_mkwctt_collection_settings,

    model_settings.OBJECT_PG_mkwctt_model_settings,
    model_settings.OBJECT_PT_mkwctt_model_settings,
    model_settings.SCENE_PG_mkwctt_model_shader_stage,
    model_settings.SCENE_PG_mkwctt_model_shader,
    model_settings.MATERIAL_PG_mkwctt_model_settings_layer,
    model_settings.MATERIAL_PG_mkwctt_model_settings,
    model_settings.MATERIAL_OT_mkwctt_model_settings_layers_action,
    model_settings.MATERIAL_OT_mkwctt_model_shader_add,
    model_settings.MATERIAL_OT_mkwctt_model_shader_remove,
    model_settings.MATERIAL_OT_mkwctt_model_shader_duplicate,
    model_settings.MATERIAL_OT_mkwctt_model_shader_stages_action,
    model_settings.MATERIAL_UL_mkwctt_model_settings_layers,
    model_settings.MATERIAL_UL_mkwctt_model_shader_stages,
    model_settings.MATERIAL_PT_mkwctt_model_settings,
    model_settings.MATERIAL_PT_mkwctt_model_settings_layers,
    model_settings.MATERIAL_PT_mkwctt_model_shader,
    model_settings.TEXTURE_PG_mkwctt_model_settings,
    model_settings.TEXTURE_PT_mkwctt_model_settings,

    collision_settings.OBJECT_PG_mkwctt_collision_settings,
    collision_settings.OBJECT_PT_mkwctt_collision_settings,
    collision_settings.MATERIAL_PG_mkwctt_collision_settings,
    collision_settings.MATERIAL_PT_mkwctt_collision_settings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Collection.mkwctt_collection_settings = bpy.props.PointerProperty(type=collection_settings.COLLECTION_PG_mkwctt_collection_settings)

    bpy.types.Material.mkwctt_collision_settings = bpy.props.PointerProperty(type=collision_settings.MATERIAL_PG_mkwctt_collision_settings)
    bpy.types.Material.mkwctt_model_settings = bpy.props.PointerProperty(type=model_settings.MATERIAL_PG_mkwctt_model_settings)

    bpy.types.Object.mkwctt_collision_settings = bpy.props.PointerProperty(type=collision_settings.OBJECT_PG_mkwctt_collision_settings)
    bpy.types.Object.mkwctt_model_settings = bpy.props.PointerProperty(type=model_settings.OBJECT_PG_mkwctt_model_settings)

    bpy.types.Scene.mkwctt_export_info = bpy.props.PointerProperty(type=export_info.SCENE_PG_mkwctt_export_info)
    bpy.types.Scene.mkwctt_race_settings = bpy.props.PointerProperty(type=track_info.SCENE_PG_mkwctt_race_settings)
    bpy.types.Scene.mkwctt_model_shaders = bpy.props.CollectionProperty(type=model_settings.SCENE_PG_mkwctt_model_shader)

    bpy.types.Texture.mkwctt_model_settings = bpy.props.PointerProperty(type=model_settings.TEXTURE_PG_mkwctt_model_settings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
