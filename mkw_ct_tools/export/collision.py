
from dataclasses import dataclass, field

import bpy

from .. import utils
from .buffer import Buffer, V3F_ORDER


@dataclass
class CollisionOutputInfo:
    size: int = 0

    face_count: int = 0
    verts: list = field(default_factory=list)
    flags: list = field(default_factory=list)


def calc_kcl_flag(obj: bpy.types.Object, mat_idx):
    collision_settings = obj.mkwctt_collision_settings
    if len(obj.material_slots) > 0:
        mat_collision_settings = obj.material_slots[mat_idx].material.mkwctt_collision_settings
        if mat_collision_settings.enable:
            collision_settings = mat_collision_settings

    kclt = utils.get_enum_number(collision_settings, 'kcl_type')
    if kclt == 0xFF:  # 'none'
        return None

    kclv = collision_settings.kcl_variant
    kcltr = 1 if collision_settings.kcl_trickable else 0
    kclnd = 1 if collision_settings.kcl_non_drivable else 0
    kclsw = 1 if collision_settings.kcl_soft_wall else 0

    return (kclsw << 15) | (kclnd << 14) | (kcltr << 13) | (kclv << 5) | kclt

def collect_objects(collection: bpy.types.Collection, scale, info: CollisionOutputInfo):
    collection_settings = collection.mkwctt_collection_settings
    if not collection_settings.has_collision:
        return

    for obj in collection.objects:
        if obj.type != 'MESH':
            continue

        collision_settings = obj.mkwctt_collision_settings
        if not collision_settings.enable:
            continue

        mesh = obj.to_mesh()
        mesh.transform(obj.matrix_world)
        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            kcl_flag = calc_kcl_flag(obj, tri.material_index)
            if kcl_flag is None:
                continue

            for vert in tri.vertices:
                info.verts.append(mesh.vertices[vert].co * scale)

            info.flags.append(kcl_flag)

            info.face_count += 1

    for coll in collection.children:
        collect_objects(coll, scale, info)

def get_output_info(context):
    info = CollisionOutputInfo()

    collect_objects(context.scene.collection, context.scene.mkwctt_export_settings.scale, info)
    info.size = 0x04 + info.face_count * 0x26

    return info


def export_collision(context, info: CollisionOutputInfo, out: Buffer):
    out.put32(info.face_count)

    for vert in info.verts:
        out.putv(vert, order=V3F_ORDER)

    for flag in info.flags:
        out.put16(flag)
