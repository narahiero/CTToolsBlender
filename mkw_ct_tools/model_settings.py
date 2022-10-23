
import bpy

from . import node_manager, utils


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


def trigger_shader_stage_nodes_update(name):
    # completely rebuild tree for now, update will be implemented later
    def func(self, context):
        for shader_idx, shader in enumerate(self.id_data.mkwctt_model_settings.shaders):
            if shader.id == self.shader_id:
                break

        node_manager.rebuild_shader_tree(context, shader)

        for material in bpy.data.materials:
            if material.mkwctt_model_settings.shader_index == shader_idx:
                node_manager.relink_material_tree(context, material)

    return func


SHADER_CO_ARGS = [
    ('out', "Pixel Output", "The value last outputted to Pixel Output, black if not set", 0x00),
    ('out_alpha', "Pixel Output Alpha", "The alpha of the value last outputted to Pixel Output, black if not set", 0x01),
    ('color_0', "Color 0", "The value of the material's color block 0", 0x02),
    ('color_0_alpha', "Color 0 Alpha", "The alpha of the value of the material's color block 0", 0x03),
    ('color_1', "Color 1", "The value of the material's color block 1", 0x04),
    ('color_1_alpha', "Color 1 Alpha", "The alpha of the value of the material's color block 1", 0x05),
    ('color_2', "Color 2", "The value of the material's color block 2", 0x06),
    ('color_2_alpha', "Color 2 Alpha", "The alpha of the value of the material's color block 2", 0x07),
    ('texture', "Texture", "The value sampled from the texture", 0x08),
    ('texture_alpha', "Texture Alpha", "The alpha of the value sampled from the texture", 0x09),
    ('raster', "Raster", "The value of the light channel (raster)", 0x0A),
    ('raster_alpha', "Raster Alpha", "The alpha of the value of the light channel (raster)", 0x0B),
    ('one', "One (White)", "One (white)", 0x0C),
    ('half', "Half (Gray)", "Half (50% gray)", 0x0D),
    ('constant', "Constant", "The value of the color constant", 0x0E),
    ('zero', "Zero (Black)", "Zero (black)", 0x0F),
]

SHADER_AO_ARGS = [
    ('out', "Pixel Output", "The alpha of the value last outputted to Pixel Output, 0 if not set", 0x00),
    ('color_0', "Color 0", "The alpha of the value of the material's color block 0", 0x01),
    ('color_1', "Color 1", "The alpha of the value of the material's color block 1", 0x02),
    ('color_2', "Color 2", "The alpha of the value of the material's color block 2", 0x03),
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
    ('color_0', "Color 0", "Output to material's color block 0", 0x01),
    ('color_1', "Color 1", "Output to material's color block 1", 0x02),
    ('color_2', "Color 2", "Output to material's color block 2", 0x03),
]


class SCENE_PG_mkwctt_model_shader_stage(bpy.types.PropertyGroup):
    id: bpy.props.IntProperty()

    shader_id: bpy.props.IntProperty()

    node_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
    )

    use_texture: bpy.props.BoolProperty(
        name="Uses Texture",
        description="Whether this stage uses a texture",
        default=False,
        update=trigger_shader_stage_nodes_update('use_texture'),
    )

    uv_map_index: bpy.props.IntProperty(
        name="UV Map Index",
        description="The index of the UV map to use to sample texture",
        min=0, max=7,
        default=0,
        update=trigger_shader_stage_nodes_update('uv_map_index'),
    )

    co_const: bpy.props.EnumProperty(
        name="Color Constant",
        description="The color constant for the color operation",
        items=[
            ('const_1_1', "Constant - 1 (White)", "100%", 0x00),
            ('const_7_8', "Constant - 7/8 (Light Gray)", "87.5%", 0x01),
            ('const_3_4', "Constant - 3/4 (Light Gray)", "75%", 0x02),
            ('const_5_8', "Constant - 5/8 (Gray)", "62.5%", 0x03),
            ('const_1_2', "Constant - 1/2 (Gray)", "50%", 0x04),
            ('const_3_8', "Constant - 3/8 (Gray)", "37.5%", 0x05),
            ('const_1_4', "Constant - 1/4 (Dark Gray)", "25%", 0x06),
            ('const_1_8', "Constant - 1/8 (Dark Gray)", "12.5%", 0x07),
            ('mat_0_rgb', "Material Color Constant 0 - RGB", "The RGB value of the material's color constant 0", 0x0C),
            ('mat_1_rgb', "Material Color Constant 1 - RGB", "The RGB value of the material's color constant 1", 0x0D),
            ('mat_2_rgb', "Material Color Constant 2 - RGB", "The RGB value of the material's color constant 2", 0x0E),
            ('mat_3_rgb', "Material Color Constant 3 - RGB", "The RGB value of the material's color constant 3", 0x0F),
            ('mat_0_rrr', "Material Color Constant 0 - Red", "The red value of the material's color constant 0", 0x10),
            ('mat_1_rrr', "Material Color Constant 1 - Red", "The red value of the material's color constant 1", 0x11),
            ('mat_2_rrr', "Material Color Constant 2 - Red", "The red value of the material's color constant 2", 0x12),
            ('mat_3_rrr', "Material Color Constant 3 - Red", "The red value of the material's color constant 3", 0x13),
            ('mat_0_ggg', "Material Color Constant 0 - Green", "The green value of the material's color constant 0", 0x14),
            ('mat_1_ggg', "Material Color Constant 1 - Green", "The green value of the material's color constant 1", 0x15),
            ('mat_2_ggg', "Material Color Constant 2 - Green", "The green value of the material's color constant 2", 0x16),
            ('mat_3_ggg', "Material Color Constant 3 - Green", "The green value of the material's color constant 3", 0x17),
            ('mat_0_bbb', "Material Color Constant 0 - Blue", "The blue value of the material's color constant 0", 0x18),
            ('mat_1_bbb', "Material Color Constant 1 - Blue", "The blue value of the material's color constant 1", 0x19),
            ('mat_2_bbb', "Material Color Constant 2 - Blue", "The blue value of the material's color constant 2", 0x1A),
            ('mat_3_bbb', "Material Color Constant 3 - Blue", "The blue value of the material's color constant 3", 0x1B),
            ('mat_0_aaa', "Material Color Constant 0 - Alpha", "The alpha value of the material's color constant 0", 0x1C),
            ('mat_1_aaa', "Material Color Constant 1 - Alpha", "The alpha value of the material's color constant 1", 0x1D),
            ('mat_2_aaa', "Material Color Constant 2 - Alpha", "The alpha value of the material's color constant 2", 0x1E),
            ('mat_3_aaa', "Material Color Constant 3 - Alpha", "The alpha value of the material's color constant 3", 0x1F),
        ],
        default='mat_0_rgb',
        update=trigger_shader_stage_nodes_update('co_const'),
    )

    co_arg_a: bpy.props.EnumProperty(
        name="Arg A",
        description="Argument 'A' for the color operation",
        items=SHADER_CO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('co_arg_a'),
    )

    co_arg_b: bpy.props.EnumProperty(
        name="Arg B",
        description="Argument 'B' for the color operation",
        items=SHADER_CO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('co_arg_b'),
    )

    co_arg_c: bpy.props.EnumProperty(
        name="Arg C",
        description="Argument 'C' for the color operation",
        items=SHADER_CO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('co_arg_c'),
    )

    co_arg_d: bpy.props.EnumProperty(
        name="Arg D",
        description="Argument 'D' for the color operation",
        items=SHADER_CO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('co_arg_d'),
    )

    co_bias: bpy.props.EnumProperty(
        name="Bias",
        items=SHADER_BIAS,
        default='zero',
        update=trigger_shader_stage_nodes_update('co_bias'),
    )

    co_op: bpy.props.EnumProperty(
        name="Op",
        items=SHADER_OP,
        default='add',
        update=trigger_shader_stage_nodes_update('co_op'),
    )

    co_clamp: bpy.props.BoolProperty(
        name="Clamp",
        default=True,
        update=trigger_shader_stage_nodes_update('co_clamp'),
    )

    co_shift: bpy.props.EnumProperty(
        name="Shift",
        items=SHADER_SHIFT,
        default='zero',
        update=trigger_shader_stage_nodes_update('co_shift'),
    )

    co_dest: bpy.props.EnumProperty(
        name="Dest",
        items=SHADER_DEST,
        default='out',
        update=trigger_shader_stage_nodes_update('co_dest'),
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
            ('mat_0_r', "Material Color Constant 0 - Red", "The red value of the material's color constant 0", 0x10),
            ('mat_1_r', "Material Color Constant 1 - Red", "The red value of the material's color constant 1", 0x11),
            ('mat_2_r', "Material Color Constant 2 - Red", "The red value of the material's color constant 2", 0x12),
            ('mat_3_r', "Material Color Constant 3 - Red", "The red value of the material's color constant 3", 0x13),
            ('mat_0_g', "Material Color Constant 0 - Green", "The green value of the material's color constant 0", 0x14),
            ('mat_1_g', "Material Color Constant 1 - Green", "The green value of the material's color constant 1", 0x15),
            ('mat_2_g', "Material Color Constant 2 - Green", "The green value of the material's color constant 2", 0x16),
            ('mat_3_g', "Material Color Constant 3 - Green", "The green value of the material's color constant 3", 0x17),
            ('mat_0_b', "Material Color Constant 0 - Blue", "The blue value of the material's color constant 0", 0x18),
            ('mat_1_b', "Material Color Constant 1 - Blue", "The blue value of the material's color constant 1", 0x19),
            ('mat_2_b', "Material Color Constant 2 - Blue", "The blue value of the material's color constant 2", 0x1A),
            ('mat_3_b', "Material Color Constant 3 - Blue", "The blue value of the material's color constant 3", 0x1B),
            ('mat_0_a', "Material Color Constant 0 - Alpha", "The alpha value of the material's color constant 0", 0x1C),
            ('mat_1_a', "Material Color Constant 1 - Alpha", "The alpha value of the material's color constant 1", 0x1D),
            ('mat_2_a', "Material Color Constant 2 - Alpha", "The alpha value of the material's color constant 2", 0x1E),
            ('mat_3_a', "Material Color Constant 3 - Alpha", "The alpha value of the material's color constant 3", 0x1F),
        ],
        default='mat_0_a',
        update=trigger_shader_stage_nodes_update('ao_const'),
    )

    ao_arg_a: bpy.props.EnumProperty(
        name="Arg A",
        description="Argument 'A' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('ao_arg_a'),
    )

    ao_arg_b: bpy.props.EnumProperty(
        name="Arg B",
        description="Argument 'B' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('ao_arg_b'),
    )

    ao_arg_c: bpy.props.EnumProperty(
        name="Arg C",
        description="Argument 'C' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('ao_arg_c'),
    )

    ao_arg_d: bpy.props.EnumProperty(
        name="Arg D",
        description="Argument 'D' for the alpha operation",
        items=SHADER_AO_ARGS,
        default='zero',
        update=trigger_shader_stage_nodes_update('ao_arg_d'),
    )

    ao_bias: bpy.props.EnumProperty(
        name="Bias",
        items=SHADER_BIAS,
        default='zero',
        update=trigger_shader_stage_nodes_update('ao_bias'),
    )

    ao_op: bpy.props.EnumProperty(
        name="Op",
        items=SHADER_OP,
        default='add',
        update=trigger_shader_stage_nodes_update('ao_op'),
    )

    ao_clamp: bpy.props.BoolProperty(
        name="Clamp",
        default=True,
        update=trigger_shader_stage_nodes_update('ao_clamp'),
    )

    ao_shift: bpy.props.EnumProperty(
        name="Shift",
        items=SHADER_SHIFT,
        default='zero',
        update=trigger_shader_stage_nodes_update('ao_shift'),
    )

    ao_dest: bpy.props.EnumProperty(
        name="Dest",
        items=SHADER_DEST,
        default='out',
        update=trigger_shader_stage_nodes_update('ao_dest'),
    )


def get_shader_name(self):
    return "" if 'name' not in self else self['name']

def set_shader_name(self, value):
    if 'name' not in self or self['name'] != value:
        self['name'] = utils.unique_name(bpy.context.scene.mkwctt_model_settings.shaders, value)

class SCENE_PG_mkwctt_model_shader(bpy.types.PropertyGroup):
    id: bpy.props.IntProperty()

    node_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
    )

    name: bpy.props.StringProperty(
        name="Name",
        description="Shader name. Must be unique",
        get=get_shader_name,
        set=set_shader_name,
    )

    stages: bpy.props.CollectionProperty(
        type=SCENE_PG_mkwctt_model_shader_stage,
    )


class SCENE_PG_mkwctt_model_settings(bpy.types.PropertyGroup):
    last_shader_id: bpy.props.IntProperty(
        default=0,
    )

    last_shader_stage_id: bpy.props.IntProperty(
        default=0,
    )

    shaders: bpy.props.CollectionProperty(
        type=SCENE_PG_mkwctt_model_shader,
    )


class NODETREE_PG_mkwctt_model_settings(bpy.types.PropertyGroup):
    tree_type: bpy.props.EnumProperty(
        items=[
            ('material', "Material", "Material"),
            ('shader', "Shader", "Shader"),
            ('stage', "Shader Stage", "Shader stage"),
        ],
        default='material',
    )

    layout: bpy.props.StringProperty(
        default='none',
    )


########### MATERIAL ###########################################################


def trigger_material_nodes_update(name):
    def func(self, context):
        node_manager.update_material_tree(context, self.id_data, name)
    return func


class MATERIAL_PG_mkwctt_model_settings_layer(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(
        type=bpy.types.Texture,
        name="Texture",
        description="The layer texture",
        poll=lambda self, texture: texture.type == 'IMAGE',
        update=trigger_material_nodes_update('texture'),
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
        update=trigger_material_nodes_update('wrap_mode'),
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
        update=trigger_material_nodes_update('mag_filter'),
    )


def get_shader_index(self):
    return 0 if 'shader_index' not in self else self['shader_index']

def set_shader_index(self, value):
    self['shader_index'] = max(min(value, len(bpy.context.scene.mkwctt_model_settings.shaders) - 1), 0)

class MATERIAL_PG_mkwctt_model_settings(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Override object model settings",
        default=True,
    )

    color: bpy.props.FloatVectorProperty(
        subtype='COLOR',
        name="Color",
        description="The color of this material in the model",
        size=3,
        min=0., max=1.,
        default=(.5, .5, .5),
        update=trigger_material_nodes_update('color'),
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
        update=trigger_material_nodes_update('shader_index'),
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

        node_manager.update_material_tree(context, context.active_object.active_material)

        return {'FINISHED'}


class MATERIAL_OT_mkwctt_model_shader_add(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_add'
    bl_label = "New"
    bl_description = "Create new shader"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        scene_model_settings = context.scene.mkwctt_model_settings
        shaders = scene_model_settings.shaders
        model_settings = context.active_object.active_material.mkwctt_model_settings

        scene_model_settings.last_shader_id += 1

        new_shader = shaders.add()
        new_shader.id = scene_model_settings.last_shader_id
        new_shader.name = utils.unique_name(shaders, "Shader")

        node_manager.rebuild_shader_tree(context, new_shader)

        model_settings.shader_index = len(shaders) - 1

        if len(shaders) > 1:
            node_manager.update_material_tree(context, context.active_object.active_material)
            node_manager.relink_material_tree(context, context.active_object.active_material)
        else:
            for material in bpy.data.materials:
                node_manager.update_material_tree(context, material)
                node_manager.relink_material_tree(context, material)

        return {'FINISHED'}


class MATERIAL_OT_mkwctt_model_shader_remove(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_remove'
    bl_label = "Delete"
    bl_description = "Delete shader"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        shaders = context.scene.mkwctt_model_settings.shaders

        model_settings = context.active_object.active_material.mkwctt_model_settings
        shaders.remove(model_settings.shader_index)

        removed_index = model_settings.shader_index
        for material in bpy.data.materials:
            if len(shaders) > 0:
                if material.mkwctt_model_settings.shader_index >= removed_index:
                    material.mkwctt_model_settings.shader_index -= 1

            node_manager.update_material_tree(context, material)
            node_manager.relink_material_tree(context, material)

        return {'FINISHED'}


class MATERIAL_OT_mkwctt_model_shader_duplicate(bpy.types.Operator):
    bl_idname = 'material.mkwctt_model_shader_duplicate'
    bl_label = "Duplicate"
    bl_description = "Duplicate shader"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        if context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        scene_model_settings = context.scene.mkwctt_model_settings
        shaders = scene_model_settings.shaders
        model_settings = context.active_object.active_material.mkwctt_model_settings

        scene_model_settings.last_shader_id += 1

        if len(shaders) == 0:
            return {'FINISHED'}

        src_shader = shaders[model_settings.shader_index]
        new_shader = shaders.add()
        new_shader.id = scene_model_settings.last_shader_id
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

        node_manager.rebuild_shader_tree(context, new_shader)

        if len(shaders) > 1:
            node_manager.update_material_tree(context, context.active_object.active_material)
            node_manager.relink_material_tree(context, context.active_object.active_material)
        else:
            for material in bpy.data.materials:
                node_manager.update_material_tree(context, material)
                node_manager.relink_material_tree(context, material)

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
        if len(context.scene.mkwctt_model_settings.shaders) == 0 or context.active_object is None or context.active_object.active_material is None:
            return {'FINISHED'}

        scene_model_settings = context.scene.mkwctt_model_settings
        model_settings = context.active_object.active_material.mkwctt_model_settings
        shader = scene_model_settings.shaders[model_settings.shader_index]

        if self.action == 'add':
            if len(shader.stages) == 8:
                self.report({'ERROR'}, "Shaders cannot have more than 8 stages each.")
                return {'FINISHED'}

            scene_model_settings.last_shader_stage_id += 1

            stage = shader.stages.add()
            stage.id = scene_model_settings.last_shader_stage_id
            stage.shader_id = shader.id
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

        node_manager.rebuild_shader_tree(context, shader)

        for material in bpy.data.materials:
            if material.mkwctt_model_settings.shader_index == model_settings.shader_index:
                node_manager.update_material_tree(context, material)
                node_manager.relink_material_tree(context, material)

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
            layout.prop(model_settings, 'color')

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

        if len(context.scene.mkwctt_model_settings.shaders) == 0:
            layout.operator('material.mkwctt_model_shader_add', icon='ADD')

        else:
            shader = context.scene.mkwctt_model_settings.shaders[model_settings.shader_index]

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
                layout.label(text="Color Operation")
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
            ('rgb565', "Color (RGB565)", "5-bit red, 6-bit green, 5-bit blue, no alpha", 0x04),
            ('rgb5a3', "Color and Alpha (RGB5A3)", "15-bit RGB and no alpha or 12-bit RGB and 3-bit alpha", 0x05),
            ('rgba8', "Color and Alpha (RGBA8)", "32-bit RGBA", 0x06),
            ('cmpr', "Compressed Color and Transparency (CMPR)", "Compressed color and 1-bit alpha", 0x0E),
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
