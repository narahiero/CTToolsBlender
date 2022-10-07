
import bpy


KCL_TYPES = [
    ('none', "None", "No collision", 0xFF),
    ('road', "Road", "Normal road", 0x00),
    ('road_extra', "Road (Extra)", "Normal road", 0x17),
    ('road_sticky', "Sticky Road", "Sticky road", 0x16),
    ('road_slip', "Slippery Road", "Slippery road, does not slow down", 0x01),
    ('road_boost', "Boost Panel", "Boost panel", 0x06),
    ('road_fall', "Solid Fall", "Out-of-bounds road", 0x0A),
    ('road_item', "Item Road", "Road only solid for items", 0x09),
    ('road_object', "Moving Road", "Road that moves objects", 0x15),
    ('road_route', "Moving Terrain", "Road that moves objects along a route", 0x0B),
    ('road_roulette', "Rotating Road", "Road, rotates objects counterclockwise", 0x1D),
    ('offroad_weak', "Weak Off-road", "Off-road, slows down slightly", 0x02),
    ('offroad', "Off-road", "Off-road, slows down", 0x03),
    ('offroad_heavy', "Heavy Off-road", "Off-road, slows down heavily", 0x04),
    ('offroad_slip', "Slippery Off-road", "Slippery off-road, slows down slightly", 0x05),
    ('ramp_boost', "Boost Ramp", "Boost ramp, trickable", 0x07),
    ('ramp_halfpipe', "Half-pipe Ramp", "Half-pipe ramp, trickable", 0x13),
    ('ramp_jump', "Jump Pad", "Jump pad, trickable", 0x08),
    ('wall', "Wall", "Wall", 0x0C),
    ('wall_extra', "Wall (Extra)", "Wall, items pass through", 0x1F),
    ('wall_weak', "Weak Wall", "Wall, can help prevent 'Bean corners'", 0x19),
    ('wall_invis', "Invisible Wall", "Wall, items pass through", 0x0D),
    ('wall_halfpipe', "Half-pipe Invisible Wall", "Wall, only solid during half-pipe jump", 0x1C),
    ('wall_player', "Player Wall", "Wall, items pass through", 0x14),
    ('wall_item', "Item Wall", "Wall, only solid for items", 0x0E),
    ('wall_nofx', "No-GFX Wall", "Wall, no GFX", 0x0F),
    ('wall_special', "Wall (Special)", "Wall with special properties", 0x1E),
    ('trigger_fall', "Fall Boundary", "Out-of-bounds plane", 0x10),
    ('trigger_cannon', "Cannon Activator", "Cannon activator", 0x11),
    ('trigger_recalc', "Force Recalculation", "Force enemy/item route recalculation", 0x12),
    ('trigger_sound', "Sound Trigger", "Sound trigger", 0x18),
    ('trigger_effect', "Effect Trigger", "Effect trigger", 0x1A),
    ('trigger_state', "Item State Modifier", "Stops items leaving conveyor belts", 0x1B),
]


########### OBJECT #############################################################


class OBJECT_PG_mkwctt_collision_settings(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Has collision",
        description="Whether this object has collision",
        default=True,
    )

    kcl_type: bpy.props.EnumProperty(
        name="Collision Type",
        description="The type of collision of this object",
        items=KCL_TYPES,
        default='none',
    )

    kcl_variant: bpy.props.IntProperty(
        name="Variant",
        description="The variant of the collision type",
        min=0, max=7, default=0,
    )

    kcl_trickable: bpy.props.BoolProperty(
        name="Trickable",
        description="Whether this object is trickable. Note: keep this unchecked if the collision type is a Boost or Half-pipe ramp",
        default=False,
    )

    kcl_non_drivable: bpy.props.BoolProperty(
        name="Non-drivable",
        description="If turned on, this setting will force the player to turn around. Has no effect on non-road collision types",
        default=False,
    )

    kcl_soft_wall: bpy.props.BoolProperty(
        name="Soft Wall",
        description="If turned on, hitting this object will not make the player bounce back. This is sometimes known as 'Barrel roll wall'",
        default=False,
    )


class OBJECT_PT_mkwctt_collision_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Collision"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'MESH'

    def draw_header(self, context):
        self.layout.prop(context.active_object.mkwctt_collision_settings, 'enable', text="")

    def draw(self, context):
        collision_settings = context.active_object.mkwctt_collision_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if collision_settings.enable:
            layout.prop(collision_settings, 'kcl_type')

            if collision_settings.kcl_type != 'none':
                layout.prop(collision_settings, 'kcl_variant')
                layout.prop(collision_settings, 'kcl_trickable')
                layout.prop(collision_settings, 'kcl_non_drivable')
                layout.prop(collision_settings, 'kcl_soft_wall')

        else:
            layout.label(text="This object does not have collision.")


########### MATERIAL ###########################################################


class MATERIAL_PG_mkwctt_collision_settings(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Has collision",
        description="Whether this material has collision settings. If off, faces with this material will use the object's collision settings",
        default=False,
    )

    kcl_type: bpy.props.EnumProperty(
        name="Collision Type",
        description="The collision type of this material",
        items=KCL_TYPES,
        default='none',
    )

    kcl_variant: bpy.props.IntProperty(
        name="Variant",
        description="The variant of the collision type",
        min=0, max=7, default=0,
    )

    kcl_trickable: bpy.props.BoolProperty(
        name="Trickable",
        description="Whether this material is trickable. Note: keep this unchecked if the collision type is a Boost or Half-pipe ramp",
        default=False,
    )

    kcl_non_drivable: bpy.props.BoolProperty(
        name="Non-drivable",
        description="If turned on, this setting will force the player to turn around. Has no effect on non-road collision types",
        default=False,
    )

    kcl_soft_wall: bpy.props.BoolProperty(
        name="Soft Wall",
        description="If turned on, hitting this material will not make the player bounce back. This is sometimes known as 'Barrel roll wall'",
        default=False,
    )


class MATERIAL_PT_mkwctt_collision_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Collision"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def draw_header(self, context):
        self.layout.prop(context.active_object.active_material.mkwctt_collision_settings, 'enable', text="")

    def draw(self, context):
        collision_settings = context.active_object.active_material.mkwctt_collision_settings

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if collision_settings.enable:
            layout.prop(collision_settings, 'kcl_type')

            if collision_settings.kcl_type != 'none':
                layout.prop(collision_settings, 'kcl_variant')
                layout.prop(collision_settings, 'kcl_trickable')
                layout.prop(collision_settings, 'kcl_non_drivable')
                layout.prop(collision_settings, 'kcl_soft_wall')

        else:
            layout.label(text="This material inherits collision settings from the object.")
