
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


class MATERIAL_PG_mkwctt_model_settings_layer(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(
        type=bpy.types.Texture,
        name="Texture",
        description="The layer texture",
        poll=lambda self, texture: texture.type == 'IMAGE',
    )

    wrap_mode: bpy.props.EnumProperty(
        name="Wrap Mode",
        description="How the texture is extended past its edges",
        items=[
            ('clamp', "Clamp", "Clamp on edges", 0x00),
            ('repeat', "Repeat", "Repeat on edges", 0x01),
            ('mirror', "Mirror", "Mirror on edges", 0x02),
        ],
        default='repeat',
    )

    min_filter: bpy.props.EnumProperty(
        name="Min Filter",
        description="How the texture is sampled when minified",
        items=[
            ('nearest', "Nearest", "Sample nearest texel", 0x00),
            ('linear', "Linear", "Linear interpolation of texels", 0x01),
            ('nearest_mipmap_nearest', "Nearest, Mipmap Nearest", "Sample nearest texel from nearest mipmap", 0x02),
            ('linear_mipmap_nearest', "Linear, Mipmap Nearest", "Sample nearest texel from linear interpolation of mipmaps", 0x03),
            ('nearest_mipmap_linear', "Nearest, Mipmap Linear", "Linear interpolation of texels from nearest mipmap", 0x04),
            ('linear_mipmap_linear', "Linear, Mipmap Linear", "Linear interpolation of texels from linear interpolation of mipmaps", 0x05),
        ],
        default='linear_mipmap_linear',
    )

    mag_filter: bpy.props.EnumProperty(
        name="Mag Filter",
        description="How the texture is sampled when magnified",
        items=[
            ('nearest', "Nearest", "Sample nearest texel", 0x00),
            ('linear', "Linear", "Linear interpolation of texels", 0x01),
        ],
        default='linear',
    )


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

    layers: bpy.props.CollectionProperty(
        type=MATERIAL_PG_mkwctt_model_settings_layer,
    )

    layer_index: bpy.props.IntProperty(
        default=0,
    )


class MATERIAL_OT_mkwctt_model_settings_layers_action(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_settings_layers_action'
    bl_label = "Material layer operations"
    bl_options = {'UNDO', 'INTERNAL'}

    action: bpy.props.EnumProperty(
        items=[
            ('add', "Add", ""),
            ('remove', "Remove", ""),
            ('up', "Up", ""),
            ('down', "Down", ""),
        ],
    )

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        model_settings = context.active_object.active_material.mkwctt_model_settings

        if self.action == 'add':
            if len(model_settings.layers) == 256:
                self.report({'ERROR'}, "Materials cannot have more than 256 layers each.")
                return {'FINISHED'}

            model_settings.layers.add()
            model_settings.layer_index = len(model_settings.layers) - 1

        elif self.action == 'remove':
            if len(model_settings.layers) == 0:
                self.report({'ERROR'}, "There are no layers to remove.")
                return {'FINISHED'}

            model_settings.layers.remove(model_settings.layer_index)

            if model_settings.layer_index > 0:
                model_settings.layer_index -= 1

        elif self.action == 'up':
            if model_settings.layer_index == 0:
                return {'FINISHED'}

            model_settings.layers.move(model_settings.layer_index, model_settings.layer_index - 1)
            model_settings.layer_index -= 1

        elif self.action == 'down':
            if model_settings.layer_index >= len(model_settings.layers) - 1:
                return {'FINISHED'}

            model_settings.layers.move(model_settings.layer_index, model_settings.layer_index + 1)
            model_settings.layer_index += 1

        return {'FINISHED'}


class MATERIAL_UL_mkwctt_model_settings_layers(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Layer {index + 1}")
        layout.prop(item, 'texture', emboss=False, text="")


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


class MATERIAL_PT_mkwctt_model_settings_layers(bpy.types.Panel):
    bl_parent_id = 'MATERIAL_PT_mkwctt_model_settings'
    bl_label = "Layers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(self, context):
        return context.active_object.active_material.mkwctt_model_settings.enable

    def draw_header(self, context):
        self.layout.label(text="", icon='RENDERLAYERS')

    def draw(self, context):
        model_settings = context.active_object.active_material.mkwctt_model_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.template_list('MATERIAL_UL_mkwctt_model_settings_layers', '', model_settings, 'layers', model_settings, 'layer_index', rows=3)

        col = row.column(align=True)
        col.operator('material.mkwctt_model_settings_layers_action', icon='ADD', text="").action = 'add'
        col.operator('material.mkwctt_model_settings_layers_action', icon='REMOVE', text="").action = 'remove'
        col.separator()
        col.operator('material.mkwctt_model_settings_layers_action', icon='TRIA_UP', text="").action = 'up'
        col.operator('material.mkwctt_model_settings_layers_action', icon='TRIA_DOWN', text="").action = 'down'

        if len(model_settings.layers) > 0:
            layer = model_settings.layers[model_settings.layer_index]

            layout.prop(layer, 'texture')
            layout.prop(layer, 'wrap_mode')
            layout.prop(layer, 'min_filter')
            layout.prop(layer, 'mag_filter')


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
