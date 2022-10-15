
import bpy

from . import utils


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


########### SHADER #############################################################


SHADER_CO_ARGS = [
    ('out', "Pixel Output", "The value last outputted to Pixel Output, black if not set", 0x00),
    ('out_alpha', "Pixel Output Alpha", "The alpha of the value last outputted to Pixel Output, black if not set", 0x01),
    ('colour_0', "Colour 0", "The value of the material's colour block 0", 0x02),
    ('colour_0_alpha', "Colour 0 Alpha", "The alpha of the value of the material's colour block 0", 0x03),
    ('colour_1', "Colour 1", "The value of the material's colour block 1", 0x04),
    ('colour_1_alpha', "Colour 1 Alpha", "The alpha of the value of the material's colour block 1", 0x05),
    ('colour_2', "Colour 2", "The value of the material's colour block 2", 0x06),
    ('colour_2_alpha', "Colour 2 Alpha", "The alpha of the value of the material's colour block 2", 0x07),
    ('texture', "Texture", "The value sampled from the texture", 0x08),
    ('texture_alpha', "Texture Alpha", "The alpha of the value sampled from the texture", 0x09),
    ('raster', "Raster", "The value of the light channel (raster)", 0x0A),
    ('raster_alpha', "Raster Alpha", "The alpha of the value of the light channel (raster)", 0x0B),
    ('one', "One (White)", "One (white)", 0x0C),
    ('half', "Half (Gray)", "Half (50% gray)", 0x0D),
    ('constant', "Constant", "The value of the colour constant", 0x0E),
    ('zero', "Zero (Black)", "Zero (black)", 0x0F),
]

SHADER_AO_ARGS = [
    ('out', "Pixel Output", "The alpha of the value last outputted to Pixel Output, 0 if not set", 0x00),
    ('colour_0', "Colour 0", "The alpha of the value of the material's colour block 0", 0x01),
    ('colour_1', "Colour 1", "The alpha of the value of the material's colour block 1", 0x02),
    ('colour_2', "Colour 2", "The alpha of the value of the material's colour block 2", 0x03),
    ('texture', "Texture", "The alpha of the value sampled from the texture", 0x04),
    ('raster', "Raster", "The alpha of the value of the light channel (raster)", 0x05),
    ('constant', "Constant", "The value of the alpha constant", 0x06),
    ('zero', "Zero", "Zero", 0x07),
]

SHADER_BIAS = [
    ('zero', "Zero", "Zero", 0x00),
    ('add', "Add Half", "0.5", 0x01),
    ('sub', "Subtract Half", "-0.5", 0x02),
    ('special', "Special Case", "Special case", 0x03),
]

SHADER_OP = [
    ('add', "+", "Add", 0x00),
    ('sub', "-", "Subtract", 0x01),
]

SHADER_SHIFT = [
    ('zero', "None", "No factor", 0x00),
    ('lshift_1', "Multiply by 2", "Multiply by 2", 0x01),
    ('lshift_2', "Multiply by 4", "Multiply by 4", 0x02),
    ('rshift_1', "Divide by 2", "Divide by 2", 0x03),
]

SHADER_DEST = [
    ('out', "Pixel Output", "Output to fragment", 0x00),
    ('colour_0', "Colour 0", "Output to material's colour block 0", 0x01),
    ('colour_1', "Colour 1", "Output to material's colour block 1", 0x02),
    ('colour_2', "Colour 2", "Output to material's colour block 2", 0x03),
]


class SCENE_PG_mkwctt_model_shader_stage(bpy.types.PropertyGroup):
    use_texture: bpy.props.BoolProperty(
        name="Uses Texture",
        description="Whether this stage uses a texture",
        default=False,
    )

    uv_map_index: bpy.props.IntProperty(
        name="UV Map Index",
        description="The index of the UV map to use to sample texture",
        min=0, max=7,
        default=0,
    )

    co_const: bpy.props.EnumProperty(
        name="Colour Constant",
        description="The colour constant for the colour operation",
        items=[
            ('const_1_1', "Constant - 1 (White)", "100%", 0x00),
            ('const_7_8', "Constant - 7/8 (Light Gray)", "87.5%", 0x01),
            ('const_3_4', "Constant - 3/4 (Light Gray)", "75%", 0x02),
            ('const_5_8', "Constant - 5/8 (Gray)", "62.5%", 0x03),
            ('const_1_2', "Constant - 1/2 (Gray)", "50%", 0x04),
            ('const_3_8', "Constant - 3/8 (Gray)", "37.5%", 0x05),
            ('const_1_4', "Constant - 1/4 (Dark Gray)", "25%", 0x06),
            ('const_1_8', "Constant - 1/8 (Dark Gray)", "12.5%", 0x07),
            ('mat_0_rgb', "Material Colour Constant 0 - RGB", "The RGB value of the material's colour constant 0", 0x0C),
            ('mat_1_rgb', "Material Colour Constant 1 - RGB", "The RGB value of the material's colour constant 1", 0x0D),
            ('mat_2_rgb', "Material Colour Constant 2 - RGB", "The RGB value of the material's colour constant 2", 0x0E),
            ('mat_3_rgb', "Material Colour Constant 3 - RGB", "The RGB value of the material's colour constant 3", 0x0F),
            ('mat_0_rrr', "Material Colour Constant 0 - Red", "The red value of the material's colour constant 0", 0x10),
            ('mat_1_rrr', "Material Colour Constant 1 - Red", "The red value of the material's colour constant 1", 0x11),
            ('mat_2_rrr', "Material Colour Constant 2 - Red", "The red value of the material's colour constant 2", 0x12),
            ('mat_3_rrr', "Material Colour Constant 3 - Red", "The red value of the material's colour constant 3", 0x13),
            ('mat_0_ggg', "Material Colour Constant 0 - Green", "The green value of the material's colour constant 0", 0x14),
            ('mat_1_ggg', "Material Colour Constant 1 - Green", "The green value of the material's colour constant 1", 0x15),
            ('mat_2_ggg', "Material Colour Constant 2 - Green", "The green value of the material's colour constant 2", 0x16),
            ('mat_3_ggg', "Material Colour Constant 3 - Green", "The green value of the material's colour constant 3", 0x17),
            ('mat_0_bbb', "Material Colour Constant 0 - Blue", "The blue value of the material's colour constant 0", 0x18),
            ('mat_1_bbb', "Material Colour Constant 1 - Blue", "The blue value of the material's colour constant 1", 0x19),
            ('mat_2_bbb', "Material Colour Constant 2 - Blue", "The blue value of the material's colour constant 2", 0x1A),
            ('mat_3_bbb', "Material Colour Constant 3 - Blue", "The blue value of the material's colour constant 3", 0x1B),
            ('mat_0_aaa', "Material Colour Constant 0 - Alpha", "The alpha value of the material's colour constant 0", 0x1C),
            ('mat_1_aaa', "Material Colour Constant 1 - Alpha", "The alpha value of the material's colour constant 1", 0x1D),
            ('mat_2_aaa', "Material Colour Constant 2 - Alpha", "The alpha value of the material's colour constant 2", 0x1E),
            ('mat_3_aaa', "Material Colour Constant 3 - Alpha", "The alpha value of the material's colour constant 3", 0x1F),
        ],
        default='mat_0_rgb',
    )

    co_arg_a: bpy.props.EnumProperty(
        name="Arg A",
        description="Argument 'A' for the colour operation",
        items=SHADER_CO_ARGS,
        default='zero',
    )

    co_arg_b: bpy.props.EnumProperty(
        name="Arg B",
        description="Argument 'B' for the colour operation",
        items=SHADER_CO_ARGS,
        default='zero',
    )

    co_arg_c: bpy.props.EnumProperty(
        name="Arg C",
        description="Argument 'C' for the colour operation",
        items=SHADER_CO_ARGS,
        default='zero',
    )

    co_arg_d: bpy.props.EnumProperty(
        name="Arg D",
        description="Argument 'D' for the colour operation",
        items=SHADER_CO_ARGS,
        default='zero',
    )

    co_bias: bpy.props.EnumProperty(
        name="Bias",
        items=SHADER_BIAS,
        default='zero',
    )

    co_op: bpy.props.EnumProperty(
        name="Op",
        items=SHADER_OP,
        default='add',
    )

    co_clamp: bpy.props.BoolProperty(
        name="Clamp",
        default=True,
    )

    co_shift: bpy.props.EnumProperty(
        name="Shift",
        items=SHADER_SHIFT,
        default='zero',
    )

    co_dest: bpy.props.EnumProperty(
        name="Dest",
        items=SHADER_DEST,
        default='out',
    )

    ao_const: bpy.props.EnumProperty(
        name="Alpha Constant",
        description="The alpha constant for the alpha operation",
        items=[
            ('const_1_1', "Constant - 1", "100%", 0x00),
            ('const_7_8', "Constant - 7/8", "87.5%", 0x01),
            ('const_3_4', "Constant - 3/4", "75%", 0x02),
            ('const_5_8', "Constant - 5/8", "62.5%", 0x03),
            ('const_1_2', "Constant - 1/2", "50%", 0x04),
            ('const_3_8', "Constant - 3/8", "37.5%", 0x05),
            ('const_1_4', "Constant - 1/4", "25%", 0x06),
            ('const_1_8', "Constant - 1/8", "12.5%", 0x07),
            ('mat_0_r', "Material Colour Constant 0 - Red", "The red value of the material's colour constant 0", 0x10),
            ('mat_1_r', "Material Colour Constant 1 - Red", "The red value of the material's colour constant 1", 0x11),
            ('mat_2_r', "Material Colour Constant 2 - Red", "The red value of the material's colour constant 2", 0x12),
            ('mat_3_r', "Material Colour Constant 3 - Red", "The red value of the material's colour constant 3", 0x13),
            ('mat_0_g', "Material Colour Constant 0 - Green", "The green value of the material's colour constant 0", 0x14),
            ('mat_1_g', "Material Colour Constant 1 - Green", "The green value of the material's colour constant 1", 0x15),
            ('mat_2_g', "Material Colour Constant 2 - Green", "The green value of the material's colour constant 2", 0x16),
            ('mat_3_g', "Material Colour Constant 3 - Green", "The green value of the material's colour constant 3", 0x17),
            ('mat_0_b', "Material Colour Constant 0 - Blue", "The blue value of the material's colour constant 0", 0x18),
            ('mat_1_b', "Material Colour Constant 1 - Blue", "The blue value of the material's colour constant 1", 0x19),
            ('mat_2_b', "Material Colour Constant 2 - Blue", "The blue value of the material's colour constant 2", 0x1A),
            ('mat_3_b', "Material Colour Constant 3 - Blue", "The blue value of the material's colour constant 3", 0x1B),
            ('mat_0_a', "Material Colour Constant 0 - Alpha", "The alpha value of the material's colour constant 0", 0x1C),
            ('mat_1_a', "Material Colour Constant 1 - Alpha", "The alpha value of the material's colour constant 1", 0x1D),
            ('mat_2_a', "Material Colour Constant 2 - Alpha", "The alpha value of the material's colour constant 2", 0x1E),
            ('mat_3_a', "Material Colour Constant 3 - Alpha", "The alpha value of the material's colour constant 3", 0x1F),
        ],
        default='mat_0_a',
    )

    ao_arg_a: bpy.props.EnumProperty(
        name="Arg A",
        description="Argument 'A' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
    )

    ao_arg_b: bpy.props.EnumProperty(
        name="Arg B",
        description="Argument 'B' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
    )

    ao_arg_c: bpy.props.EnumProperty(
        name="Arg C",
        description="Argument 'C' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
    )

    ao_arg_d: bpy.props.EnumProperty(
        name="Arg D",
        description="Argument 'D' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
    )

    ao_bias: bpy.props.EnumProperty(
        name="Bias",
        items=SHADER_BIAS,
        default='zero',
    )

    ao_op: bpy.props.EnumProperty(
        name="Op",
        items=SHADER_OP,
        default='add',
    )

    ao_clamp: bpy.props.BoolProperty(
        name="Clamp",
        default=True,
    )

    ao_shift: bpy.props.EnumProperty(
        name="Shift",
        items=SHADER_SHIFT,
        default='zero',
    )

    ao_dest: bpy.props.EnumProperty(
        name="Dest",
        items=SHADER_DEST,
        default='out',
    )


def get_shader_name(self):
    return "" if 'name' not in self else self['name']

def set_shader_name(self, value):
    if 'name' not in self or self['name'] != value:
        self['name'] = utils.unique_name(bpy.context.scene.mkwctt_model_shaders, value)

class SCENE_PG_mkwctt_model_shader(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        description="Shader name. Must be unique",
        get=get_shader_name,
        set=set_shader_name,
    )

    stages: bpy.props.CollectionProperty(
        type=SCENE_PG_mkwctt_model_shader_stage,
    )


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


def get_shader_index(self):
    return 0 if 'shader_index' not in self else self['shader_index']

def set_shader_index(self, value):
    self['shader_index'] = max(min(value, len(bpy.context.scene.mkwctt_model_shaders) - 1), 0)

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

    shader_stage_index: bpy.props.IntProperty(
        default=0,
    )

    shader_index: bpy.props.IntProperty(
        name="Shader Index",
        min=0,
        default=0,
        get=get_shader_index,
        set=set_shader_index,
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


class MATERIAL_OT_mkwctt_model_shader_add(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_add'
    bl_label = "New"
    bl_description = "Create new shader"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        shaders = context.scene.mkwctt_model_shaders
        model_settings = context.active_object.active_material.mkwctt_model_settings

        new_shader = shaders.add()
        new_shader.name = utils.unique_name(shaders, "Shader")

        model_settings.shader_index = len(shaders) - 1

        return {'FINISHED'}


class MATERIAL_OT_mkwctt_model_shader_remove(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_remove'
    bl_label = "Delete"
    bl_description = "Delete shader"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        model_settings = context.active_object.active_material.mkwctt_model_settings
        context.scene.mkwctt_model_shaders.remove(model_settings.shader_index)

        if model_settings.shader_index > 0:
            model_settings.shader_index -= 1

        return {'FINISHED'}


class MATERIAL_OT_mkwctt_model_shader_duplicate(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_duplicate'
    bl_label = "Duplicate"
    bl_description = "Duplicate shader"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        shaders = context.scene.mkwctt_model_shaders
        model_settings = context.active_object.active_material.mkwctt_model_settings

        src_shader = shaders[model_settings.shader_index]
        new_shader = shaders.add()

        new_shader.name = utils.unique_name(shaders, src_shader.name)

        for src_stage in src_shader.stages:
            new_stage: SCENE_PG_mkwctt_model_shader_stage = new_shader.stages.add()

            new_stage.use_texture = src_stage.use_texture
            new_stage.uv_map_index = src_stage.uv_map_index

            new_stage.co_const = src_stage.co_const
            new_stage.co_arg_a = src_stage.co_arg_a
            new_stage.co_arg_b = src_stage.co_arg_b
            new_stage.co_arg_c = src_stage.co_arg_c
            new_stage.co_arg_d = src_stage.co_arg_d
            new_stage.co_bias = src_stage.co_bias
            new_stage.co_op = src_stage.co_op
            new_stage.co_clamp = src_stage.co_clamp
            new_stage.co_shift = src_stage.co_shift
            new_stage.co_dest = src_stage.co_dest

            new_stage.ao_const = src_stage.ao_const
            new_stage.ao_arg_a = src_stage.ao_arg_a
            new_stage.ao_arg_b = src_stage.ao_arg_b
            new_stage.ao_arg_c = src_stage.ao_arg_c
            new_stage.ao_arg_d = src_stage.ao_arg_d
            new_stage.ao_bias = src_stage.ao_bias
            new_stage.ao_op = src_stage.ao_op
            new_stage.ao_clamp = src_stage.ao_clamp
            new_stage.ao_shift = src_stage.ao_shift
            new_stage.ao_dest = src_stage.ao_dest

        model_settings.shader_index = len(shaders) - 1

        return {'FINISHED'}


class MATERIAL_OT_mkwctt_model_shader_stages_action(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_stages_action'
    bl_label = "Shader stage operations"
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
        if len(context.scene.mkwctt_model_shaders) == 0 or context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        model_settings = context.active_object.active_material.mkwctt_model_settings
        shader = context.scene.mkwctt_model_shaders[model_settings.shader_index]

        if self.action == 'add':
            if len(shader.stages) == 8:
                self.report({'ERROR'}, "Shaders cannot have more than 8 stages each.")
                return {'FINISHED'}

            shader.stages.add()
            model_settings.shader_stage_index = len(shader.stages) - 1

        elif self.action == 'remove':
            if len(shader.stages) == 0:
                self.report({'ERROR'}, "There are no stages to remove.")
                return {'FINISHED'}

            shader.stages.remove(model_settings.shader_stage_index)

            if model_settings.shader_stage_index > 0:
                model_settings.shader_stage_index -= 1

        elif self.action == 'up':
            if model_settings.shader_stage_index == 0:
                return {'FINISHED'}

            shader.stages.move(model_settings.shader_stage_index, model_settings.shader_stage_index - 1)
            model_settings.shader_stage_index -= 1

        elif self.action == 'down':
            if model_settings.shader_stage_index >= len(shader.stages) - 1:
                return {'FINISHED'}

            shader.stages.move(model_settings.shader_stage_index, model_settings.shader_stage_index + 1)
            model_settings.shader_stage_index += 1

        return {'FINISHED'}


class MATERIAL_UL_mkwctt_model_settings_layers(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Layer {index}")
        layout.prop(item, 'texture', emboss=False, text="")


class MATERIAL_UL_mkwctt_model_shader_stages(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"Stage {index}")


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


class MATERIAL_PT_mkwctt_model_shader(bpy.types.Panel):
    bl_parent_id = 'MATERIAL_PT_mkwctt_model_settings'
    bl_label = "Shader"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(self, context):
        return context.active_object.active_material.mkwctt_model_settings.enable

    def draw_header(self, context):
        self.layout.label(text="", icon='SHADING_RENDERED')

    def draw(self, context):
        model_settings = context.active_object.active_material.mkwctt_model_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if len(context.scene.mkwctt_model_shaders) == 0:
            layout.operator('material.mkwctt_model_shader_add', icon='ADD')

        else:
            shader = context.scene.mkwctt_model_shaders[model_settings.shader_index]

            split = layout.split(factor=1/6, align=True)
            split.prop(model_settings, 'shader_index', icon_only=True)
            split = split.split(factor=4/5, align=True)
            split.prop(shader, 'name', icon_only=True)
            split.operator('material.mkwctt_model_shader_duplicate', text="", icon='DUPLICATE')
            split.operator('material.mkwctt_model_shader_remove', text="", icon='PANEL_CLOSE')
            split.operator('material.mkwctt_model_shader_add', text="", icon='ADD')

            layout.separator(factor=.75)
            layout.label(text="Stages", icon='NODE_COMPOSITING')

            row = layout.row()
            row.template_list('MATERIAL_UL_mkwctt_model_shader_stages', '', shader, 'stages', model_settings, 'shader_stage_index', rows=3)

            col = row.column(align=True)
            col.operator('material.mkwctt_model_shader_stages_action', icon='ADD', text="").action = 'add'
            col.operator('material.mkwctt_model_shader_stages_action', icon='REMOVE', text="").action = 'remove'
            col.separator()
            col.operator('material.mkwctt_model_shader_stages_action', icon='TRIA_UP', text="").action = 'up'
            col.operator('material.mkwctt_model_shader_stages_action', icon='TRIA_DOWN', text="").action = 'down'

            if len(shader.stages) > 0:
                stage = shader.stages[model_settings.shader_stage_index]

                layout.prop(stage, 'use_texture')
                layout.prop(stage, 'uv_map_index')

                layout.separator(factor=.75)
                layout.label(text="Colour Operation")
                layout.prop(stage, 'co_const')
                layout.prop(stage, 'co_arg_a')
                layout.prop(stage, 'co_arg_b')
                layout.prop(stage, 'co_arg_c')
                layout.prop(stage, 'co_arg_d')
                layout.prop(stage, 'co_bias')
                layout.prop(stage, 'co_op', expand=True)
                layout.prop(stage, 'co_clamp')
                layout.prop(stage, 'co_shift')
                layout.prop(stage, 'co_dest')

                layout.separator(factor=.75)
                layout.label(text="Alpha Operation")
                layout.prop(stage, 'ao_const')
                layout.prop(stage, 'ao_arg_a')
                layout.prop(stage, 'ao_arg_b')
                layout.prop(stage, 'ao_arg_c')
                layout.prop(stage, 'ao_arg_d')
                layout.prop(stage, 'ao_bias')
                layout.prop(stage, 'ao_op', expand=True)
                layout.prop(stage, 'ao_clamp')
                layout.prop(stage, 'ao_shift')
                layout.prop(stage, 'ao_dest')


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
