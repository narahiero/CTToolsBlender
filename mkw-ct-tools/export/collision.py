
from dataclasses import dataclass, field

import bpy

from . import utils
from .buffer import Buffer, V3F_ORDER


@dataclass
class ObjectCollisionOutputInfo:
    off: int = 0
    size: int = 0

    obj: bpy.types.Object = None
    count: int = 0


@dataclass
class CollisionOutputInfo:
    size: int = 0

    objs: list = field(default_factory=list)
    face_count: int = 0


def collect_objects(collection: bpy.types.Collection, info: CollisionOutputInfo):
    collection_settings = collection.mkwctt_collection_settings
    if not collection_settings.has_collision:
        return

    for obj in collection.objects:
        if obj.type != 'MESH':
            continue

        collision_settings = obj.mkwctt_collision_settings
        if not collision_settings.enable or collision_settings.kcl_type == 'none':
            continue

        obj_info = ObjectCollisionOutputInfo()
        obj_info.obj = obj

        mesh = obj.to_mesh()
        mesh.calc_loop_triangles()
        obj_info.count = len(mesh.loop_triangles)
        info.face_count += obj_info.count

        obj_info.off = info.size
        obj_info.size = 0x08 + obj_info.count * 0x24

        info.size += obj_info.size
        info.objs.append(obj_info)

    for coll in collection.children:
        collect_objects(coll, info)

def get_output_info(context):
    info = CollisionOutputInfo()

    collect_objects(context.scene.collection, info)

    header_size = 0x08 + len(info.objs) * 0x04
    info.size += header_size

    for obj_info in info.objs:
        obj_info.off += header_size

    return info


def write_object(obj_info: ObjectCollisionOutputInfo, scale, out: Buffer):
    out.put32(obj_info.count)

    obj = obj_info.obj
    collision_settings = obj.mkwctt_collision_settings
    kclt = utils.get_enum_number(collision_settings, 'kcl_type')
    kclv = collision_settings.kcl_variant
    kcltr = 1 if collision_settings.kcl_trickable else 0
    kclnd = 1 if collision_settings.kcl_non_drivable else 0
    kclsw = 1 if collision_settings.kcl_soft_wall else 0
    kcl_flag = (kclsw << 15) | (kclnd << 14) | (kcltr << 13) | (kclv << 5) | kclt
    out.put16(kcl_flag)
    out.put16(0)  # padding

    mesh = obj.to_mesh()
    mesh.transform(obj.matrix_world)
    mesh.calc_loop_triangles()
    for tri in mesh.loop_triangles:
        for vertex in tri.vertices:
            out.putv(mesh.vertices[vertex].co * scale, order=V3F_ORDER)

def export_collision(context, info: CollisionOutputInfo, out: Buffer):
    export_info = context.scene.mkwctt_export_info

    count = len(info.objs)
    out.put32(count)
    out.put32(info.face_count)

    for obj_info in info.objs:
        out.put32(obj_info.off)
        write_object(obj_info, export_info.scale, out.slice(off=obj_info.off, size=obj_info.size))
