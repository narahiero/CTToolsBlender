
from dataclasses import dataclass, field
from unicodedata import name

import bpy

from . import utils
from .buffer import Buffer, V3F_ORDER, V3F_SCALE_ORDER
from .string_table import StringTable


@dataclass
class ModelTextureOutputInfo:
    off: int = 0
    size: int = 0
    use_count: int = 0

    tex: bpy.types.Texture = None
    name_off: int = 0


@dataclass
class ModelMaterialOutputInfo:
    off: int = 0
    use_count: int = 0

    mat: bpy.types.Material = None
    name_off: int = 0


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

    parts_off: int = 0
    parts: dict = field(default_factory=dict)


@dataclass
class ModelOutputInfo:
    off: int = 0
    size: int = 0

    texs_off: int = 0
    texs: dict = field(default_factory=dict)

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

def collect_materials(scene: bpy.types.Scene, info: ModelsOutputInfo, string_table: StringTable):
    for obj in scene.objects:
        for mat_slot in obj.material_slots:
            for model_info in info.models:
                if mat_slot.name in model_info.mats or not mat_slot.material.mkwctt_model_settings.enable:
                    continue

                mat_info = ModelMaterialOutputInfo()
                mat_info.mat = mat_slot.material
                mat_info.name_off = string_table[mat_slot.name]
                model_info.mats[mat_slot.name] = mat_info

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
            vset.add(vert.co.copy().freeze())
            nset.add(vert.normal.copy().freeze())

        obj_info.verts = list(vset)
        obj_info.norms = list(nset)

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
            part_info.mat_name_off = string_table["___Default___"]
            part_info.size = 0x0C
            obj_info.parts[0] = part_info

        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            if tri.material_index not in obj_info.parts:
                continue

            part_info = obj_info.parts[tri.material_index]
            for vert in reversed(tri.vertices):  # blender draws ccw while wii draws cw
                part_info.inds.append((
                    obj_info.verts.index(mesh.vertices[vert].co),
                    obj_info.norms.index(mesh.vertices[vert].normal),
                ))

            part_info.size += 0x0C

        for mat_idx in list(obj_info.parts.keys()):
            if len(obj_info.parts[mat_idx].inds) == 0:
                del obj_info.parts[mat_idx]

        if len(obj_info.parts) == 0:
            continue

        obj_info.size = 0x34

        obj_info.verts_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.verts) * 0x0C

        obj_info.norms_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.norms) * 0x0C

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

def get_output_info(context, string_table):
    info = ModelsOutputInfo()

    info.models.append(ModelOutputInfo())  # course model
    info.models.append(ModelOutputInfo())  # skybox model

    collect_textures(context.blend_data, info, string_table)
    collect_materials(context.scene, info, string_table)
    collect_objects(context.scene.collection, info, string_table)

    info.size = 0x08

    for model_info in info.models:
        model_info.size = 0x0C

        model_info.texs_off = model_info.size
        texs_size = 0x04 + len(model_info.texs) * 0x04
        for tex_info in model_info.texs.values():
            tex_info.off = texs_size
            texs_size += tex_info.size
        model_info.size += texs_size

        for mat_name in list(model_info.mats.keys()):
            if model_info.mats[mat_name].use_count == 0:
                del model_info.mats[mat_name]

        model_info.mats_off = model_info.size
        mats_size = 0x04 + len(model_info.mats) * 0x04
        for mat_info in model_info.mats.values():
            mat_info.off = mats_size
            mats_size += 0x08
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

def write_material(mat_info: ModelMaterialOutputInfo, out: Buffer):
    model_settings = mat_info.mat.mkwctt_model_settings

    out.put32(mat_info.name_off)

    for comp in model_settings.colour:
        out.put8(int(comp * 0xFF))
    out.put8(0xFF)  # padding (alpha/unused)

def write_part(part_info: ModelPartOutputInfo, out: Buffer):
    out.put32(part_info.name_off)
    out.put32(part_info.mat_name_off)

    write_inds_array(part_info.inds, out)

def write_v3f_array(data, scale, out: Buffer):
    out.put32(len(data))
    for vec in data:
        out.putv(vec * scale, order=V3F_ORDER)

def write_inds_array(data, out: Buffer):
    out.put8(0x90)  # wii graphics code draw triangles command byte
    out.put16(len(data))
    for vert in data:
        for idx in vert:
            out.put16(idx)
    out.put8(0)  # padding

def write_object(obj_info: ModelObjectOutputInfo, scale, out: Buffer):
    out.put32(obj_info.name_off)
    out.put32(obj_info.verts_off)
    out.put32(obj_info.norms_off)
    out.put32(obj_info.parts_off)

    out.putv(obj_info.obj.location * scale, order=V3F_ORDER)
    out.putv(obj_info.obj.rotation_euler, order=V3F_ORDER)
    out.putv(obj_info.obj.scale, order=V3F_SCALE_ORDER)

    write_v3f_array(obj_info.verts, scale, out.slice(off=obj_info.verts_off))
    write_v3f_array(obj_info.norms, 1., out.slice(off=obj_info.norms_off))

    out = out.slice(off=obj_info.parts_off)
    out.put32(len(obj_info.parts))
    for part_info in obj_info.parts.values():
        out.put32(part_info.off)
        write_part(part_info, out.slice(off=part_info.off))

def write_model(model_info: ModelOutputInfo, scale, out: Buffer):
    out.put32(model_info.texs_off)
    out.put32(model_info.mats_off)
    out.put32(model_info.objs_off)

    out.pos = model_info.texs_off
    out.put32(len(model_info.texs))
    for tex_info in model_info.texs.values():
        out.put32(tex_info.off)
        write_texture(tex_info, out)

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
    export_info = context.scene.mkwctt_export_info

    for model_info in info.models:
        out.put32(model_info.off)
        write_model(model_info, export_info.scale, out.slice(off=model_info.off, size=model_info.size))
