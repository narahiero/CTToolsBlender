
import bpy


class SCENE_PG_mkwctt_race_settings(bpy.types.PropertyGroup):
    track_slot: bpy.props.EnumProperty(
        name="Track Slot",
        description="The track slot this custom track replaces",
        items=[
            ('1.1', "1.1: Luigi Circuit",               "Luigi Circuit",               0x08),
            ('1.2', "1.2: Moo Moo Meadows",             "Moo Moo Meadows",             0x01),
            ('1.3', "1.3: Mushroom Gorge",              "Mushroom Gorge",              0x02),
            ('1.4', "1.4: Toad's Factory",              "Toad's Factory",              0x04),

            ('2.1', "2.1: Mario Circuit",               "Mario Circuit",               0x00),
            ('2.2', "2.2: Coconut Mall",                "Coconut Mall",                0x05),
            ('2.3', "2.3: DK Summit",                   "DK Summit",                   0x06),
            ('2.4', "2.4: Wario's Gold Mine",           "Wario's Gold Mine",           0x07),

            ('3.1', "3.1: Daisy Circuit",               "Daisy Circuit",               0x09),
            ('3.2', "3.2: Koopa Cape",                  "Koopa Cape",                  0x0F),
            ('3.3', "3.3: Maple Treeway",               "Maple Treeway",               0x0B),
            ('3.4', "3.4: Grumble Volcano",             "Grumble Volcano",             0x03),

            ('4.1', "4.1: Dry Dry Ruins",               "Dry Dry Ruins",               0x0E),
            ('4.2', "4.2: Moonview Highway",            "Moonview Highway",            0x0A),
            ('4.3', "4.3: Bowser's Castle",             "Bowser's Castle",             0x0C),
            ('4.4', "4.4: Rainbow Road",                "Rainbow Road",                0x0D),

            ('5.1', "5.1: GCN Peach Beach",             "GCN Peach Beach",             0x10),
            ('5.2', "5.2: DS Yoshi Falls",              "DS Yoshi Falls",              0x14),
            ('5.3', "5.3: SNES Ghost Valley 2",         "SNES Ghost Valley 2",         0x19),
            ('5.4', "5.4: N64 Mario Raceway",           "N64 Mario Raceway",           0x1A),

            ('6.1', "6.1: N64 Shertbet Land",           "N64 Shertbet Land",           0x1B),
            ('6.2', "6.2: GBA Shy Guy Beach",           "GBA Shy Guy Beach",           0x1F),
            ('6.3', "6.3: DS Delfino Square",           "DS Delfino Square",           0x17),
            ('6.4', "6.4: GCN Waluigi Stadium",         "GCN Waluigi Stadium",         0x12),

            ('7.1', "7.1: DS Desert Hills",             "DS Desert Hills",             0x15),
            ('7.2', "7.2: GBA Bowser Castle 3",         "GBA Bowser Castle 3",         0x1E),
            ('7.3', "7.3: N64 DK's Jungle Parkway",     "N64 DK's Jungle Parkway",     0x1D),
            ('7.4', "7.4: GCN Mario Circuit",           "GCN Mario Circuit",           0x11),

            ('8.1', "8.1: SNES Mario Ciruit 3",         "SNES Mario Ciruit 3",         0x18),
            ('8.2', "8.2: DS Peach Gardens",            "DS Peach Gardens",            0x16),
            ('8.3', "8.3: GCN DK Mountain",             "GCN DK Mountain",             0x13),
            ('8.4', "8.4: N64 Bowser's Castle",         "N64 Bowser's Castle",         0x1C),
        ],
        default='1.1',
    )

    lap_count: bpy.props.IntProperty(
        name="Lap Count",
        description="The number of laps to complete to finish the race. Note: A cheat code or mod pack allowing custom lap count is necessary for this to work in-game",
        min=1, max=9, default=3,
    )

    start_point: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Race Start",
        description="The position and angle where players start the race",
    )

    start_side: bpy.props.EnumProperty(
        name="Start Side",
        description="The side of the finish line which the player in first starts",
        items=[
            ('left', "Left", "Left", 0x00),
            ('right', "Right", "Right", 0x01),
        ],
        default='left',
    )


class SCENE_PT_mkwctt_race_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Race Configuration"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        race_settings = context.scene.mkwctt_race_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(race_settings, 'track_slot')
        layout.prop(race_settings, 'lap_count')
        layout.prop(race_settings, 'start_point')
        layout.prop(race_settings, 'start_side', expand=True)
