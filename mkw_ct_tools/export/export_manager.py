
from dataclasses import dataclass, field
import os

import bpy

from . import collision
from . import model
from . import track_info
from . import utils
from .buffer import Buffer
from .error import ExportError
from .string_table import StringTable


FILE_NAME_BY_ID = [
    'castle_course',
    'farm_course',
    'kinoko_course',
    'volcano_course',
    'factory_course',
    'shopping_course',
    'boardcross_course',
    'truck_course',
    'beginner_course',
    'senior_course',
    'ridgehighway_course',
    'treehouse_course',
    'koopa_course',
    'rainbow_course',
    'desert_course',
    'water_course',
    'old_peach_gc',
    'old_mario_gc',
    'old_waluigi_gc',
    'old_donkey_gc',
    'old_falls_ds',
    'old_desert_ds',
    'old_garden_ds',
    'old_town_ds',
    'old_mario_sfc',
    'old_obake_sfc',
    'old_mario_64',
    'old_sherbet_64',
    'old_koopa_64',
    'old_donkey_64',
    'old_koopa_gba',
    'old_heyho_gba',
]


@dataclass
class OutputInfo:
    total_size: int = 0

    track_output_off: int = 0
    track_output_info: track_info.TrackOutputInfo = None

    models_output_off: int = 0
    models_output_info: model.ModelsOutputInfo = None

    collision_output_off: int = 0
    collision_output_info: collision.CollisionOutputInfo = None

    string_table_off: int = 0
    string_table: StringTable = field(default_factory=StringTable)


def get_output_info(context):
    output_info = OutputInfo()
    output_info.total_size = 0x10

    output_info.track_output_off = output_info.total_size
    output_info.track_output_info = track_info.get_output_info(context)
    output_info.total_size += output_info.track_output_info.size

    output_info.models_output_off = output_info.total_size
    output_info.models_output_info = model.get_output_info(context, output_info.string_table)
    output_info.total_size += output_info.models_output_info.size

    output_info.collision_output_off = output_info.total_size
    output_info.collision_output_info = collision.get_output_info(context)
    output_info.total_size += output_info.collision_output_info.size

    output_info.string_table_off = output_info.total_size
    output_info.total_size += output_info.string_table.total_len

    return output_info

def export_string_table(string_table: StringTable, out: Buffer):
    for string in string_table.strings.keys():
        out.puts(string, nt=True)

def write(context, outdir, out: Buffer):
    track_slot_id = utils.get_enum_number(context.scene.mkwctt_race_settings, 'track_slot')
    filepath = outdir + FILE_NAME_BY_ID[track_slot_id] + '.szs.data'
    with open(filepath, 'wb') as file:
        file.write(out.data)

    import subprocess
    subprocess.run(["H:/Coding/VSCode/MKW/CTToolsBlender/build/Source/Debug/SZSBuilder.exe", filepath])

def export(context, outdir):
    if not os.path.isdir(outdir):
        raise ExportError(f"The path '{outdir}' does not exist or is not a directory.")

    output_info = get_output_info(context)

    out = Buffer(size=output_info.total_size)

    out.put32(output_info.track_output_off)
    out.put32(output_info.models_output_off)
    out.put32(output_info.collision_output_off)
    out.put32(output_info.string_table_off)

    out.pos = output_info.track_output_off
    track_info.export_track_info(context, out.slice(size=output_info.track_output_info.size))

    out.pos = output_info.models_output_off
    model.export_models(context, output_info.models_output_info, out.slice(size=output_info.models_output_info.size))

    out.pos = output_info.collision_output_off
    collision.export_collision(context, output_info.collision_output_info, out.slice(size=output_info.collision_output_info.size))

    out.pos = output_info.string_table_off
    export_string_table(output_info.string_table, out.slice(size=output_info.string_table.total_len))

    write(context, outdir, out)
