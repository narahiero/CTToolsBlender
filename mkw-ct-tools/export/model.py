
from dataclasses import dataclass, field

import bpy

from . import utils
from .buffer import Buffer, V3F_ORDER, V3F_SCALE_ORDER
from .string_table import StringTable


@dataclass
class ObjectModelOutputInfo:
    off: int = 0
    size: int = 0

    obj: bpy.types.Object = None
    name_off: int = 0

    verts_off: int = 0
    verts: list = field(default_factory=list)

    norms_off: int = 0
    norms: list = field(default_factory=list)

    inds_off: int = 0
    inds: list = field(default_factory=list)


@dataclass
class ModelOutputInfo:
    off: int = 0
    size: int = 0

    objs: list = field(default_factory=list)


@dataclass
class ModelsOutputInfo:
    size: int = 0

    models: list = field(default_factory=list)


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

        obj_info = ObjectModelOutputInfo()
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

        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            for vert in reversed(tri.vertices):  # blender draws ccw while wii draws cw
                obj_info.inds.append((
                    obj_info.verts.index(mesh.vertices[vert].co),
                    obj_info.norms.index(mesh.vertices[vert].normal),
                ))

        obj_info.size = 0x38

        obj_info.verts_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.verts) * 0x0C

        obj_info.norms_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.norms) * 0x0C

        obj_info.inds_off = obj_info.size
        obj_info.size += 0x04 + len(obj_info.inds) * 0x04

        obj_info.off = model_info.size
        model_info.size += obj_info.size
        model_info.objs.append(obj_info)

def get_output_info(context, string_table):
    info = ModelsOutputInfo()

    info.models.append(ModelOutputInfo())  # course model
    info.models.append(ModelOutputInfo())  # skybox model

    collect_objects(context.collection, info, string_table)

    info.size = 0x08

    for model_info in info.models:
        off_table_size = 0x04 + len(model_info.objs) * 0x04
        model_info.size += off_table_size

        for obj_info in model_info.objs:
            obj_info.off += off_table_size

        model_info.off = info.size
        info.size += model_info.size

    return info


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

def write_object(obj_info: ObjectModelOutputInfo, scale, out: Buffer):
    out.put32(obj_info.name_off)
    out.put32(obj_info.verts_off)
    out.put32(obj_info.norms_off)
    out.put32(obj_info.inds_off)

    out.putv(obj_info.obj.location * scale, order=V3F_ORDER)
    out.putv(obj_info.obj.rotation_euler, order=V3F_ORDER)
    out.putv(obj_info.obj.scale, order=V3F_SCALE_ORDER)

    colour = obj_info.obj.mkwctt_model_settings.colour
    for comp in colour:
        out.put8(int(comp * 0xFF))
    out.put8(0xFF)  # padding (alpha/unused)

    write_v3f_array(obj_info.verts, scale, out.slice(off=obj_info.verts_off))
    write_v3f_array(obj_info.norms, 1., out.slice(off=obj_info.norms_off))
    write_inds_array(obj_info.inds, out.slice(off=obj_info.inds_off))

def write_model(model_info: ModelOutputInfo, scale, out: Buffer):
    count = len(model_info.objs)
    out.put32(count)

    for obj_info in model_info.objs:
        out.put32(obj_info.off)
        write_object(obj_info, scale, out.slice(off=obj_info.off, size=obj_info.size))

def export_models(context, info: ModelsOutputInfo, out: Buffer):
    export_info = context.scene.mkwctt_export_info

    for model_info in info.models:
        out.put32(model_info.off)
        write_model(model_info, export_info.scale, out.slice(off=model_info.off, size=model_info.size))
