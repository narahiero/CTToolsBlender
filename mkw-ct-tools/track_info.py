
import bpy


class SCENE_PG_mkwctt_race_settings(bpy.types.PropertyGroup):
    lap_count: bpy.props.IntProperty(
        name="Lap Count",
        description="The number of laps to complete to finish the race. Note: A cheat code or mod pack allowing custom lap count is necessary for this to work in-game",
        min=1, max=9, default=3
    )


class SCENE_PT_mkwctt_race_settings(bpy.types.Panel):
    bl_label = "MKW CT Tools: Race Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        layout.prop(scene.mkwctt_race_settings, 'lap_count')
