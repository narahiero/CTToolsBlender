
import bpy


########### OBJECT #############################################################


class OBJECT_PG_mkwctt_model_settings(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Is part of model",
        description="Whether this object is part of course model",
        default=True,
    )


class OBJECT_PT_mkwctt_model_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Model Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'MESH'

    def draw_header(self, context):
        self.layout.prop(context.active_object.mkwctt_model_settings, 'enable', text="")

    def draw(self, context):
        model_settings = context.active_object.mkwctt_model_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if model_settings.enable:
            layout.label(text="This object is included in the course model.")

        else:
            layout.label(text="This object is not included in the course model.")


########### MATERIAL ###########################################################


class MATERIAL_PG_mkwctt_model_settings(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Override object model settings",
        default=True,
    )

    colour: bpy.props.FloatVectorProperty(
        subtype='COLOR',
        name="Colour",
        description="The colour of this material in the model",
        size=3,
        min=0., max=1.,
        default=(.5, .5, .5),
    )


class MATERIAL_PT_mkwctt_model_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Model Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def draw_header(self, context):
        self.layout.prop(context.active_object.active_material.mkwctt_model_settings, 'enable', text="")

    def draw(self, context):
        model_settings = context.active_object.active_material.mkwctt_model_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if model_settings.enable:
            layout.prop(model_settings, 'colour')

        else:
            layout.label(text="Faces with this material are not included in the course model.")
