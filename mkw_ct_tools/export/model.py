
from dataclasses import dataclass, field

import bpy
from mathutils import Vector

from ..model_settings import SCENE_PG_mkwctt_model_shader

from .. import utils
from .buffer import Buffer, V3F_ORDER, V3F_SCALE_ORDER
from .string_table import StringTable


DEFAULT_RESOURCE_NAME = "___Default___"


@dataclass
class ModelTextureOutputInfo:
    off: int = 0
    size: int = 0
    use_count: int = 0

    tex: bpy.types.Texture = None
    name_off: int = 0


@dataclass
class ModelShaderOutputInfo:
    off: int = 0
    size: int = 0
    use_count: int = 0

    shader: SCENE_PG_mkwctt_model_shader = None
    name_off: int = 0


@dataclass
class ModelMaterialOutputInfo:
    off: int = 0
    size: int = 0
    use_count: int = 0

    mat: bpy.types.Material = None
    name_off: int = 0

    layer_name_offs: list = field(default_factory=list)
    shader_name_off: int = 0


@dataclass
class ModelPartOutputInfo:
    off: int = 0
    size: int = 0

    name_off: int = 0
    mat_name_off: int = 0

    inds: list = field(default_factory=list)


@dataclass
class ModelObjectOutputInfo:
    off: int = 0
    size: int = 0

    obj: bpy.types.Object = None
    name_off: int = 0

    verts_off: int = 0
    verts: list = field(default_factory=list)

    norms_off: int = 0
    norms: list = field(default_factory=list)

    colors_off: int = 0
    colors: list = field(default_factory=list)

    texcoords_off: int = 0
    texcoords: list = field(default_factory=list)

    parts_off: int = 0
    parts: dict = field(default_factory=dict)


@dataclass
class ModelOutputInfo:
    off: int = 0
    size: int = 0

    texs_off: int = 0
    texs: dict = field(default_factory=dict)

    shaders_off: int = 0
    shaders: dict = field(default_factory=dict)

    mats_off: int = 0
    mats: dict = field(default_factory=dict)

    objs_off: int = 0
    objs: list = field(default_factory=list)


@dataclass
class ModelsOutputInfo:
    size: int = 0

    models: list = field(default_factory=list)


def collect_textures(data: bpy.types.BlendData, info: ModelsOutputInfo, string_table: StringTable):
    for texture in data.textures:
        if texture.type != 'IMAGE':
            continue

        image = texture.image
        for model_info in info.models:
            tex_info = ModelTextureOutputInfo()
            tex_info.tex = texture
            tex_info.name_off = string_table[texture.name]
            tex_info.size = 0x10 + image.size[0] * image.size[1] * 0x04
            model_info.texs[texture.name] = tex_info

def collect_shaders(scene: bpy.types.Scene, info: ModelsOutputInfo, string_table: StringTable):
    for shader in scene.mkwctt_model_settings.shaders:
        for model_info in info.models:
            shader_info = ModelShaderOutputInfo()
            shader_info.shader = shader
            shader_info.name_off = string_table[shader.name]
            shader_info.size = 0x08 + len(shader.stages) * 0x18
            model_info.shaders[shader.name] = shader_info

def collect_materials(scene: bpy.types.Scene, info: ModelsOutputInfo, string_table: StringTable):
    for obj in scene.objects:
        for mat_slot in obj.material_slots:
            mat = mat_slot.material
            model_settings = mat.mkwctt_model_settings
            if not model_settings.enable:
                continue

            for model_info in info.models:
                if mat.name in model_info.mats:
                    continue

                mat_info = ModelMaterialOutputInfo()
                mat_info.mat = mat
                mat_info.name_off = string_table[mat.name]
                mat_info.size = 0x10 + len(model_settings.layers) * 0x08
                model_info.mats[mat.name] = mat_info

                for layer in model_settings.layers:
                    if layer.texture is not None:
                        tex_name = layer.texture.name
                        model_info.texs[tex_name].use_count += 1
                    else:
                        tex_name = DEFAULT_RESOURCE_NAME
                    mat_info.layer_name_offs.append(string_table[tex_name])

                if len(model_info.shaders) > 0:
                    shader_name = scene.mkwctt_model_settings.shaders[model_settings.shader_index].name
                    model_info.shaders[shader_name].use_count += 1
                else:
                    shader_name = DEFAULT_RESOURCE_NAME
                mat_info.shader_name_off = string_table[shader_name]

def collect_objects(collection: bpy.types.Collection, info: ModelsOutputInfo, string_table: StringTable):
    collection_settings = collection.mkwctt_collection_settings
    if not collection_settings.has_model:
        return

    if not collection_settings.is_skybox:
        model_info = info.models[0]
    else:
        model_info = info.models[1]

    for obj in collection.objects:
        if obj.type != 'MESH':
            continue

        model_settings = obj.mkwctt_model_settings
        if not model_settings.enable:
            continue

        obj_info = ModelObjectOutputInfo()
        obj_info.obj = obj
        obj_info.name_off = string_table[obj.name]

        mesh = obj.to_mesh()

        vset = set()
        nset = set()
        for vert in mesh.vertices:
            vset.add(Vector(vert.co).freeze())
            nset.add(Vector(vert.normal).freeze())

        obj_info.verts = list(vset)
        obj_info.norms = list(nset)

        for color_layer in mesh.vertex_colors:
            cset = set()
            for color in color_layer.data:
                cset.add(Vector(color.color).freeze())

            obj_info.colors.append(list(cset))
            if len(obj_info.colors) == 2:
                break  # mdl0 support up to 2 vertex color layers per object

        for uv_layer in mesh.uv_layers:
            uvset = set()
            for uv in uv_layer.data:
                uvset.add(Vector(uv.uv).freeze())

            obj_info.texcoords.append(list(uvset))
            if len(obj_info.texcoords) == 8:
                break  # mdl0 support up to 8 texture coord layers per object

        if len(obj.material_slots) > 0:
            for mat_slot in obj.material_slots:
                if mat_slot.name not in model_info.mats:
                    continue

                part_info = ModelPartOutputInfo()
                part_info.name_off = string_table[obj.name + "___" + mat_slot.name]
                part_info.mat_name_off = string_table[mat_slot.name]
                part_info.size = 0x0C
                obj_info.parts[mat_slot.slot_index] = part_info

        else:
            part_info = ModelPartOutputInfo()
            part_info.name_off = string_table[obj.name]
            part_info.mat_name_off = string_table[DEFAULT_RESOURCE_NAME]
            part_info.size = 0x0C
            obj_info.parts[0] = part_info

        idx_size = 0x04 + len(obj_info.colors) * 0x02 + len(obj_info.texcoords) * 0x02

        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            if tri.material_index not in obj_info.parts:
                continue

            part_info = obj_info.parts[tri.material_index]
            for vert, loop in zip(reversed(tri.vertices), reversed(tri.loops)):  # blender draws ccw while wii draws cw
                idx = [
                    obj_info.verts.index(Vector(mesh.vertices[vert].co)),
                    obj_info.norms.index(Vector(mesh.vertices[vert].normal)),
                ]
                for layer_idx, layer in enumerate(obj_info.colors):
                    idx.append(layer.index(Vector(mesh.vertex_colors[layer_idx].data[loop].color)))
                for layer_idx, layer in enumerate(obj_info.texcoords):
                    idx.append(layer.index(Vector(mesh.uv_layers[layer_idx].data[loop].uv)))
                part_info.inds.append(idx)

            part_info.size += idx_size * 3

        for mat_idx in list(obj_info.parts.keys()):
            if len(obj_info.parts[mat_idx].inds) == 0:
                del obj_info.parts[mat_idx]

        if len(obj_info.parts) == 0:
            continue

        obj_info.size = 0x3C

        obj_info.verts_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.verts) * 0x0C

        obj_info.norms_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.norms) * 0x0C

        obj_info.colors_off = obj_info.size
        obj_info.size += 0x04
        for color_layer in obj_info.colors:
            obj_info.size += 0x04 + len(color_layer) * 0x04

        obj_info.texcoords_off = obj_info.size
        obj_info.size += 0x04
        for texcoord_layer in obj_info.texcoords:
            obj_info.size += 0x04 + len(texcoord_layer) * 0x08

        obj_info.parts_off = obj_info.size
        parts_size = 0x04 + len(obj_info.parts) * 0x04
        for mat_idx, part_info in obj_info.parts.items():
            if len(obj.material_slots) > 0:
                model_info.mats[obj.material_slots[mat_idx].name].use_count += 1
            part_info.off = parts_size
            parts_size += part_info.size
        obj_info.size += parts_size

        model_info.objs.append(obj_info)

    for coll in collection.children:
        collect_objects(coll, info, string_table)

def drop_unused_assets(model_info: ModelOutputInfo, string_table: StringTable):
    for mat_name in list(model_info.mats.keys()):
        mat = model_info.mats[mat_name]
        if mat.use_count == 0:
            for name_off in mat.layer_name_offs:
                tex_name = string_table[name_off]
                if tex_name != DEFAULT_RESOURCE_NAME:
                    model_info.texs[tex_name].use_count -= 1

            shader_name = string_table[mat.shader_name_off]
            if shader_name != DEFAULT_RESOURCE_NAME:
                model_info.shaders[shader_name].use_count -= 1

            del model_info.mats[mat_name]

    for shader_name in list(model_info.shaders.keys()):
        if model_info.shaders[shader_name].use_count == 0:
            del model_info.shaders[shader_name]

    for tex_name in list(model_info.texs.keys()):
        if model_info.texs[tex_name].use_count == 0:
            del model_info.texs[tex_name]

def get_output_info(context, string_table: StringTable):
    info = ModelsOutputInfo()

    info.models.append(ModelOutputInfo())  # course model
    info.models.append(ModelOutputInfo())  # skybox model

    collect_textures(context.blend_data, info, string_table)
    collect_shaders(context.scene, info, string_table)
    collect_materials(context.scene, info, string_table)
    collect_objects(context.scene.collection, info, string_table)

    info.size = 0x08

    for model_info in info.models:
        drop_unused_assets(model_info, string_table)

        model_info.size = 0x10

        model_info.texs_off = model_info.size
        texs_size = 0x04 + len(model_info.texs) * 0x04
        for tex_info in model_info.texs.values():
            tex_info.off = texs_size
            texs_size += tex_info.size
        model_info.size += texs_size

        model_info.shaders_off = model_info.size
        shaders_size = 0x04 + len(model_info.shaders) * 0x04
        for shader_info in model_info.shaders.values():
            shader_info.off = shaders_size
            shaders_size += shader_info.size
        model_info.size += shaders_size

        model_info.mats_off = model_info.size
        mats_size = 0x04 + len(model_info.mats) * 0x04
        for mat_info in model_info.mats.values():
            mat_info.off = mats_size
            mats_size += mat_info.size
        model_info.size += mats_size

        model_info.objs_off = model_info.size
        objs_size = 0x04 + len(model_info.objs) * 0x04
        for obj_info in model_info.objs:
            obj_info.off = objs_size
            objs_size += obj_info.size
        model_info.size += objs_size

        model_info.off = info.size
        info.size += model_info.size

    return info


def write_texture(tex_info: ModelTextureOutputInfo, out: Buffer):
    model_settings = tex_info.tex.mkwctt_model_settings

    out.put32(tex_info.name_off)
    out.put32(tex_info.tex.image.size[0])
    out.put32(tex_info.tex.image.size[1])

    out.put8(utils.get_enum_number(model_settings, 'format'))
    out.put8(1 if model_settings.gen_mipmaps else 0)
    out.put8(model_settings.gen_mipmap_count)
    out.put8(0)  # padding

    for comp in tex_info.tex.image.pixels:
        out.put8(int(comp * 0xFF))

def write_shader(shader_info: ModelShaderOutputInfo, out: Buffer):
    shader = shader_info.shader

    out.put32(shader_info.name_off)

    out.put32(len(shader.stages))
    for stage in shader.stages:
        out.put8(1 if stage.use_texture else 0)
        out.put8(stage.uv_map_index)
        out.put16(0)  # padding
        out.put8(utils.get_enum_number(stage, 'co_const'))
        out.put8(utils.get_enum_number(stage, 'co_arg_a'))
        out.put8(utils.get_enum_number(stage, 'co_arg_b'))
        out.put8(utils.get_enum_number(stage, 'co_arg_c'))
        out.put8(utils.get_enum_number(stage, 'co_arg_d'))
        out.put8(utils.get_enum_number(stage, 'co_bias'))
        out.put8(utils.get_enum_number(stage, 'co_op'))
        out.put8(1 if stage.co_clamp else 0)
        out.put8(utils.get_enum_number(stage, 'co_shift'))
        out.put8(utils.get_enum_number(stage, 'co_dest'))
        out.put8(utils.get_enum_number(stage, 'ao_const'))
        out.put8(utils.get_enum_number(stage, 'ao_arg_a'))
        out.put8(utils.get_enum_number(stage, 'ao_arg_b'))
        out.put8(utils.get_enum_number(stage, 'ao_arg_c'))
        out.put8(utils.get_enum_number(stage, 'ao_arg_d'))
        out.put8(utils.get_enum_number(stage, 'ao_bias'))
        out.put8(utils.get_enum_number(stage, 'ao_op'))
        out.put8(1 if stage.ao_clamp else 0)
        out.put8(utils.get_enum_number(stage, 'ao_shift'))
        out.put8(utils.get_enum_number(stage, 'ao_dest'))

def write_material(mat_info: ModelMaterialOutputInfo, out: Buffer):
    model_settings = mat_info.mat.mkwctt_model_settings

    out.put32(mat_info.name_off)
    out.put32(mat_info.shader_name_off)

    for comp in model_settings.color:
        out.put8(int(comp * 0xFF) & 0xFF)
    out.put8(0xFF)  # padding (alpha/unused)

    out.put32(len(model_settings.layers))

    for layer_index, layer in enumerate(model_settings.layers):
        out.put32(mat_info.layer_name_offs[layer_index])
        out.put8(utils.get_enum_number(layer, 'wrap_mode'))
        out.put8(utils.get_enum_number(layer, 'min_filter'))
        out.put8(utils.get_enum_number(layer, 'mag_filter'))
        out.put8(0)  # padding

def write_v3f_array(data, scale, out: Buffer):
    out.put32(len(data))
    for vec in data:
        out.putv(vec * scale, order=V3F_ORDER)

def write_color_array(data, out: Buffer):
    out.put32(len(data))
    for vec in data:
        for comp in vec:
            out.put8(int(comp * 0xFF) & 0xFF)

def write_uv_array(data, out: Buffer):
    out.put32(len(data))
    for vec in data:
        out.putv(vec)

def write_inds_array(data, out: Buffer):
    out.put8(0x90)  # wii graphics code draw triangles command byte
    out.put16(len(data))
    for vert in data:
        for idx in vert:
            out.put16(idx)
    out.put8(0)  # padding

def write_part(part_info: ModelPartOutputInfo, out: Buffer):
    out.put32(part_info.name_off)
    out.put32(part_info.mat_name_off)

    write_inds_array(part_info.inds, out)

def write_object(obj_info: ModelObjectOutputInfo, scale, out: Buffer):
    out.put32(obj_info.name_off)
    out.put32(obj_info.verts_off)
    out.put32(obj_info.norms_off)
    out.put32(obj_info.colors_off)
    out.put32(obj_info.texcoords_off)
    out.put32(obj_info.parts_off)

    out.putv(obj_info.obj.location * scale, order=V3F_ORDER)
    out.putv(obj_info.obj.rotation_euler, order=V3F_ORDER)
    out.putv(obj_info.obj.scale, order=V3F_SCALE_ORDER)

    write_v3f_array(obj_info.verts, scale, out.slice(off=obj_info.verts_off))
    write_v3f_array(obj_info.norms, 1., out.slice(off=obj_info.norms_off))

    out.pos = obj_info.colors_off
    out.put32(len(obj_info.colors))
    for color_layer in obj_info.colors:
        write_color_array(color_layer, out)

    out.pos = obj_info.texcoords_off
    out.put32(len(obj_info.texcoords))
    for texcoord_layer in obj_info.texcoords:
        write_uv_array(texcoord_layer, out)

    out = out.slice(off=obj_info.parts_off)
    out.put32(len(obj_info.parts))
    for part_info in obj_info.parts.values():
        out.put32(part_info.off)
        write_part(part_info, out.slice(off=part_info.off))

def write_model(model_info: ModelOutputInfo, scale, out: Buffer):
    out.put32(model_info.texs_off)
    out.put32(model_info.shaders_off)
    out.put32(model_info.mats_off)
    out.put32(model_info.objs_off)

    out.pos = model_info.texs_off
    out.put32(len(model_info.texs))
    for tex_info in model_info.texs.values():
        out.put32(tex_info.off)
        write_texture(tex_info, out.slice(off=model_info.texs_off + tex_info.off))

    out.pos = model_info.shaders_off
    out.put32(len(model_info.shaders))
    for shader_info in model_info.shaders.values():
        out.put32(shader_info.off)
        write_shader(shader_info, out.slice(off=model_info.shaders_off + shader_info.off))

    out.pos = model_info.mats_off

    out.put32(len(model_info.mats))
    for mat_info in model_info.mats.values():
        out.put32(mat_info.off)
        write_material(mat_info, out.slice(off=model_info.mats_off + mat_info.off))

    out.pos = model_info.objs_off
    out.put32(len(model_info.objs))
    for obj_info in model_info.objs:
        out.put32(obj_info.off)
        write_object(obj_info, scale, out.slice(off=model_info.objs_off + obj_info.off))

def export_models(context, info: ModelsOutputInfo, out: Buffer):
    export_settings = context.scene.mkwctt_export_settings

    for model_info in info.models:
        out.put32(model_info.off)
        write_model(model_info, export_settings.scale, out.slice(off=model_info.off, size=model_info.size))
