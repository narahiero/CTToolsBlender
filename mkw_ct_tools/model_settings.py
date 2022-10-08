
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


########### TEXTURE ############################################################


class TEXTURE_PG_mkwctt_model_settings(bpy.types.PropertyGroup):
    format: bpy.props.EnumProperty(
        name="Format",
        description="The format of the image in the model",
        items=[
            ('i4', "Grayscale (I4)", "4-bit grayscale, no alpha", 0x00),
            ('i8', "Grayscale (I8)", "8-bit grayscale, no alpha", 0x01),
            ('ia4', "Grayscale and Alpha (IA4)", "4-bit grayscale and 4-bit alpha", 0x02),
            ('ia8', "Grayscale and Alpha (IA8)", "8-bit grayscale and 8-bit alpha", 0x03),
            ('rgb565', "Colour (RGB565)", "5-bit red, 6-bit green, 5-bit blue, no alpha", 0x04),
            ('rgb5a3', "Colour and Alpha (RGB5A3)", "15-bit RGB and no alpha or 12-bit RGB and 3-bit alpha", 0x05),
            ('rgba8', "Colour and Alpha (RGBA8)", "32-bit RGBA", 0x06),
            ('cmpr', "Compressed Colour and Transparency (CMPR)", "Compressed colour and 1-bit alpha", 0x0E),
        ],
        default='cmpr',
    )

    gen_mipmaps: bpy.props.BoolProperty(
        name="Generate Mipmaps",
        description="Whether or not to automatically generate mipmaps",
        default=False,
    )

    gen_mipmap_count: bpy.props.IntProperty(
        name="Mipmap count",
        description="The number of mipmaps to generate",
        min=1, max=7,
        default=1,
    )


class TEXTURE_PT_mkwctt_model_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Texture Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        return context.texture is not None

    def draw(self, context):
        model_settings = context.texture.mkwctt_model_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(model_settings, 'format')
        layout.prop(model_settings, 'gen_mipmaps')
        if model_settings.gen_mipmaps:
            layout.prop(model_settings, 'gen_mipmap_count')
