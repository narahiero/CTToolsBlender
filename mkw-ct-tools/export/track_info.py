
from dataclasses import dataclass

import bpy
from mathutils import Vector

from . import utils
from .buffer import Buffer, V3F_ORDER


@dataclass
class TrackOutputInfo:
    size: int


def get_output_info(context):
    return TrackOutputInfo(0x1C)


def export_track_info(context, out: Buffer):
    export_info = context.scene.mkwctt_export_info
    race_settings = context.scene.mkwctt_race_settings

    out.put8(utils.get_enum_number(race_settings, 'track_slot'))
    out.put8(race_settings.lap_count)
    out.put8(utils.get_enum_number(race_settings, 'start_side'))
    out.put8(0) # padding

    start_point = race_settings.start_point
    if start_point is None:
        print("WARNING: the starting point was not assigned, using a default value instead: pos=(x=0, y=0, z=0) and rot=(x=0, y=0, z=0)")
        start_pos = Vector((0, 0, 0))
        start_rot = Vector((0, 0, 0))
    else:
        start_pos = start_point.location * export_info.scale
        start_rot = start_point.rotation_euler

    out.putv(start_pos, order=V3F_ORDER)
    out.putv(start_rot, order=V3F_ORDER)
