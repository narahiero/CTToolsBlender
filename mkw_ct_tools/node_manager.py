
import bpy

from . import utils


########### GENERAL ############################################################


def make_rgb_node(tree, name, location, color = None):
    node = tree.nodes.new('ShaderNodeRGB')
    node.name = name
    node.location = location
    node.outputs[0].default_value = color if color is not None else (0.0, 0.0, 0.0, 0.0)
    return node

def make_mix_rgb_node(tree, name, location, mode, a, b):
    node = tree.nodes.new('ShaderNodeMixRGB')
    node.name = name
    node.location = location
    node.blend_type = mode
    node.inputs[0].default_value = 1.0
    tree.links.new(a, node.inputs[1])
    tree.links.new(b, node.inputs[2])
    return node


def is_property(arg: str, property: str):
    return arg == '__all__' or arg == property


########### MATERIAL ###########################################################


def rebuild_material_tree(context: bpy.types.Context, material: bpy.types.Material):
    """Completely rebuild material node tree from scratch."""

    material.use_nodes = True

    scene_model_settings = context.scene.mkwctt_model_settings
    model_settings = material.mkwctt_model_settings

    tree = material.node_tree
    tree.nodes.clear()

    texture_node = tree.nodes.new('ShaderNodeTexImage')
    texture_node.name = 'texture'
    texture_node.location = (0, 500)

    raster_node = tree.nodes.new('ShaderNodeVertexColor')
    raster_node.name = 'raster'
    raster_node.layer_name = "Col"  # hard-coded for now
    raster_node.location = (0, 100)

    make_rgb_node(tree, 'color', (0, -200))

    shader_node = tree.nodes.new('ShaderNodeGroup')
    shader_node.name = 'shader'
    shader_node.location = (400, 0)
    shader_node.width = 300
    if len(scene_model_settings.shaders) > 0:
        shader_node.node_tree = scene_model_settings.shaders[model_settings.shader_index].node_tree

    mat_out = tree.nodes.new('ShaderNodeOutputMaterial')
    mat_out.name = 'mat_out'
    mat_out.location = (800, 0)

def get_material_layout(context: bpy.types.Context, material: bpy.types.Material):
    """Return the name of the layout needed based on shader and material settings."""

    scene_model_settings = context.scene.mkwctt_model_settings

    if len(scene_model_settings.shaders) > 0:
        return 'shader'
    else:
        return 'basic'

def relink_material_tree(context: bpy.types.Context, material: bpy.types.Material):
    """Relink material nodes, rebuild if necessary."""

    material.use_nodes = True

    tree = material.node_tree
    tree_settings = tree.mkwctt_model_settings
    if tree_settings.layout == 'none':
        rebuild_material_tree(context, material)

    tree_settings.layout = get_material_layout(context, material)
    tree.links.clear()

    if tree_settings.layout == 'shader':
        texture_node = tree.nodes['texture']
        raster_node = tree.nodes['raster']
        color_node = tree.nodes['color']
        shader_node = tree.nodes['shader']
        tree.links.new(texture_node.outputs[0], shader_node.inputs[0])
        tree.links.new(raster_node.outputs[0], shader_node.inputs[1])
        tree.links.new(color_node.outputs[0], shader_node.inputs[2])

        mat_out = tree.nodes['mat_out']
        tree.links.new(shader_node.outputs[0], mat_out.inputs[0])

        tree_settings.layout = 'shader'

    elif tree_settings.layout == 'basic':
        color_node = tree.nodes['color']
        mat_out = tree.nodes['mat_out']
        tree.links.new(color_node.outputs[0], mat_out.inputs[0])

        tree_settings.layout = 'basic'

def update_material_tree(context: bpy.types.Context, material: bpy.types.Material, property = '__all__'):
    """Update material nodes, rebuild if needed."""

    material.use_nodes = True

    tree = material.node_tree
    tree_settings = tree.mkwctt_model_settings
    if tree_settings.layout == 'none':
        rebuild_material_tree(context, material)

    scene_model_settings = context.scene.mkwctt_model_settings
    model_settings = material.mkwctt_model_settings

    if is_property(property, 'color'):
        tree.nodes['color'].outputs[0].default_value = list(model_settings.color) + [1.0]

    if is_property(property, 'shader_index') and len(scene_model_settings.shaders) > 0:
        tree.nodes['shader'].node_tree = scene_model_settings.shaders[model_settings.shader_index].node_tree

    if len(model_settings.layers) > 0:
        layer = model_settings.layers[0]  # only 1 layer supported currently

        if is_property(property, 'texture') and layer.texture is not None:
            tree.nodes['texture'].image = layer.texture.image

        if is_property(property, 'wrap_mode'):
            # there is no option for mirror, so use repeat instead
            if layer.wrap_mode == 'clamp':
                ext_mode = 'EXTEND'
            else:
                ext_mode = 'REPEAT'
            tree.nodes['texture'].extension = ext_mode

        if is_property(property, 'mag_filter'):
            if layer.mag_filter == 'nearest':
                interp = 'Closest'
            else:
                interp = 'Linear'
            tree.nodes['texture'].interpolation = interp

    if tree_settings.layout != get_material_layout(context, material):
        relink_material_tree(context, material)


########### SHADER #############################################################


def rebuild_shader_stage_tree(context: bpy.types.Context, stage):
    tree_name = "MKW Model Shader Stage " + str(stage.id)

    if bpy.data.node_groups.find(tree_name) == -1:
        stage.node_tree = bpy.data.node_groups.new(tree_name, 'ShaderNodeTree')

    elif stage.node_tree == None:
        stage.node_tree = bpy.data.node_groups.get(tree_name)

    x_pos = 0

    tree = stage.node_tree
    tree.nodes.clear()
    tree.inputs.clear()
    tree.outputs.clear()

    tree_in = tree.nodes.new('NodeGroupInput')
    tree_in.location = (x_pos, 400)
    tree.inputs.new('NodeSocketColor', "Pixel Output")
    tree.inputs.new('NodeSocketColor', "Color 0")
    tree.inputs.new('NodeSocketColor', "Color 1")
    tree.inputs.new('NodeSocketColor', "Color 2")
    tree.inputs.new('NodeSocketColor', "Texture")
    tree.inputs.new('NodeSocketColor', "Raster")
    tree.inputs.new('NodeSocketColor', "Material Constant 0")
    tree.inputs.new('NodeSocketColor', "Material Constant 1")
    tree.inputs.new('NodeSocketColor', "Material Constant 2")
    tree.inputs.new('NodeSocketColor', "Material Constant 3")

    zero_node = make_rgb_node(tree, 'zero', (x_pos,    0), (0.0, 0.0, 0.0, 1.0))
    half_node = make_rgb_node(tree, 'half', (x_pos, -200), (0.5, 0.5, 0.5, 1.0))
    one_node  = make_rgb_node(tree, 'one', (x_pos, -400), (1.0, 1.0, 1.0, 1.0))

    const_sel = utils.get_enum_number(stage, 'co_const')
    if const_sel < 0x08:
        i = (8 - const_sel) / 8
        const_node = make_rgb_node(tree, 'const', (x_pos, -600), (i, i, i, i))
        color_const = const_node.outputs[0]
    else:
        color_const = tree_in.outputs[6]

    x_pos += 300

    def arg_input(arg):
        if arg.endswith('_alpha'):
            arg = arg[:-6]  # alpha channel not supported yet

        if arg == 'out':
            return tree_in.outputs[0]
        if arg == 'color_0':
            return tree_in.outputs[1]
        if arg == 'color_1':
            return tree_in.outputs[2]
        if arg == 'color_2':
            return tree_in.outputs[3]
        if arg == 'texture':
            if not stage.use_texture:
                return zero_node.outputs[0]
            return tree_in.outputs[4]
        if arg == 'raster':
            return tree_in.outputs[5]
        if arg == 'one':
            return one_node.outputs[0]
        if arg == 'half':
            return half_node.outputs[0]
        if arg == 'constant':
            return color_const
        if arg == 'zero':
            return zero_node.outputs[0]

    arg_a = arg_input(stage.co_arg_a)
    arg_b = arg_input(stage.co_arg_b)
    arg_c = arg_input(stage.co_arg_c)
    arg_d = arg_input(stage.co_arg_d)

    if stage.co_bias != 'special':
        if stage.co_bias != 'zero':
            bias_mode = 'ADD' if stage.co_bias == 'add' else 'SUBTRACT'
            d_plus_bias = make_mix_rgb_node(tree, 'd_plus_bias', (x_pos, 0), bias_mode, arg_d, half_node.outputs[0])
            op_lhs = d_plus_bias.outputs[0]

            x_pos += 200

        else:
            op_lhs = arg_d

        b_minus_a   = make_mix_rgb_node(tree, 'b_minus_a', (x_pos,       100), 'SUBTRACT', arg_b, arg_a)
        ans_times_c = make_mix_rgb_node(tree, 'ans_times_c', (x_pos + 200,   0), 'MULTIPLY', b_minus_a.outputs[0], arg_c)
        a_plus_ans  = make_mix_rgb_node(tree, 'a_plus_ans', (x_pos + 400, 100), 'ADD', arg_a, ans_times_c.outputs[0])

        x_pos += 600

        op_mode = 'ADD' if stage.co_op == 'add' else 'SUBTRACT'
        op_node = make_mix_rgb_node(tree, 'op', (x_pos, 0), op_mode, op_lhs, a_plus_ans.outputs[0])

        color_shift = utils.get_enum_number(stage, 'co_shift')
        if color_shift != 0x00:
            x_pos += 200

            shift_factor = color_shift * 2.0 if color_shift < 0x03 else 0.5
            shift_factor_node = make_rgb_node(tree, 'shift_factor', (x_pos, 0), (shift_factor, shift_factor, shift_factor, 1.0))

            x_pos += 200

            shift_node = make_mix_rgb_node(tree, 'shift', (x_pos, 0), 'MULTIPLY', shift_factor_node.outputs[0], op_node.outputs[0])

            last_node = shift_node

        else:
            last_node = op_node

        if stage.co_clamp:
            last_node.use_clamp = True

    else:  # special case not implemented yet
        last_node = zero_node

    x_pos += 300

    tree_out = tree.nodes.new('NodeGroupOutput')
    tree_out.location = (x_pos, 0)
    tree.outputs.new('NodeSocketColor', "Pixel Output")
    tree.outputs.new('NodeSocketColor', "Color 0")
    tree.outputs.new('NodeSocketColor', "Color 1")
    tree.outputs.new('NodeSocketColor', "Color 2")

    color_dest = utils.get_enum_number(stage, 'co_dest')
    for out_idx in range(4):
        node_in = tree_in.outputs[out_idx] if out_idx != color_dest else last_node.outputs[0]
        tree.links.new(node_in, tree_out.inputs[out_idx])

def rebuild_shader_tree(context: bpy.types.Context, shader):
    tree_name = "MKW Model Shader " + str(shader.id)

    if bpy.data.node_groups.find(tree_name) == -1:
        shader.node_tree = bpy.data.node_groups.new(tree_name, 'ShaderNodeTree')

    elif shader.node_tree == None:
        shader.node_tree = bpy.data.node_groups.get(tree_name)

    tree = shader.node_tree
    tree.nodes.clear()
    tree.inputs.clear()
    tree.outputs.clear()

    x_pos = 0

    tree_in = tree.nodes.new('NodeGroupInput')
    tree_in.name = 'shader_in'
    tree_in.location = (x_pos, 0)
    tree.inputs.new('NodeSocketColor', "Texture")
    tree.inputs.new('NodeSocketColor', "Raster")
    tree.inputs.new('NodeSocketColor', "Material Constant 0")
    tree.inputs.new('NodeSocketColor', "Material Constant 1")
    tree.inputs.new('NodeSocketColor', "Material Constant 2")
    tree.inputs.new('NodeSocketColor', "Material Constant 3")

    black_node = make_rgb_node(tree, 'black', (x_pos, 200), (0.0, 0.0, 0.0, 0.0))

    x_pos += 300

    tree_out = tree.nodes.new('NodeGroupOutput')
    tree_out.name = 'shader_out'
    tree.outputs.new('NodeSocketColor', "Color")

    if len(shader.stages) > 0:
        first_group = None
        prev_group = None
        for stage_idx, stage in enumerate(shader.stages):
            rebuild_shader_stage_tree(context, stage)

            group = shader.node_tree.nodes.new('ShaderNodeGroup')
            group.name = 'stage_' + str(stage_idx)
            group.location = (x_pos, 100)
            group.width = 300
            group.node_tree = stage.node_tree

            if prev_group is not None:
                tree.links.new(prev_group.outputs[0], group.inputs[0])
                tree.links.new(prev_group.outputs[1], group.inputs[1])
                tree.links.new(prev_group.outputs[2], group.inputs[2])
                tree.links.new(prev_group.outputs[3], group.inputs[3])

            tree.links.new(tree_in.outputs[0], group.inputs[4])
            tree.links.new(tree_in.outputs[1], group.inputs[5])
            tree.links.new(tree_in.outputs[2], group.inputs[6])
            tree.links.new(tree_in.outputs[3], group.inputs[7])
            tree.links.new(tree_in.outputs[4], group.inputs[8])
            tree.links.new(tree_in.outputs[5], group.inputs[9])

            prev_group = group

            if first_group is None:
                first_group = group

            x_pos += 400

        tree.links.new(black_node.outputs[0], first_group.inputs[0])
        tree.links.new(black_node.outputs[0], first_group.inputs[1])
        tree.links.new(black_node.outputs[0], first_group.inputs[2])
        tree.links.new(black_node.outputs[0], first_group.inputs[3])

        tree_out.location = (x_pos, 0)
        tree.links.new(prev_group.outputs[0], tree_out.inputs[0])

    else:
        tree_out.location = (x_pos, 0)
        tree.links.new(black_node.outputs[0], tree_out.inputs[0])
