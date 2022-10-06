
import bpy


class COLLECTION_PG_mkwctt_collection_settings(bpy.types.PropertyGroup):
    has_model: bpy.props.BoolProperty(
        name="Objects are part of model",
        description="Whether the objects within this collection will appear in course model",
        default=True,
    )

    is_skybox: bpy.props.BoolProperty(
        name="Is background",
        description="Whether the objects within this collection are part of the background",
        default=False,
    )

    has_collision: bpy.props.BoolProperty(
        name="Objects can have collision",
        description="Whether the objects within this collection can have collision",
        default=True,
    )


class COLLECTION_PT_mkwctt_collection_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Collection Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        collection_settings = context.collection.mkwctt_collection_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(collection_settings, 'has_model')
        if collection_settings.has_model:
            layout.prop(collection_settings, 'is_skybox')
        layout.prop(collection_settings, 'has_collision')
