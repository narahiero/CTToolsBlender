
import bpy

from .export import ExportError, export_manager


class SCENE_PG_mkwctt_export_info(bpy.types.PropertyGroup):
    scale: bpy.props.FloatProperty(
        name="Track Scale",
        description="The factor to multiply vertex coordinates by",
        min=0., default=1000.,
        precision=0,
    )


class SCENE_OT_mkwctt_export(bpy.types.Operator):
    bl_idname = 'scene.mkwctt_export'
    bl_label = "Export"
    bl_description = "Export this blender project as an SZS archive"

    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            export_manager.export(context, self.directory)
        except ExportError as ex:
            self.report({'ERROR'}, ex.args[0])
        return {'FINISHED'}


class SCENE_PT_mkwctt_export_info(bpy.types.Panel):
    bl_label = "MKW CT Tools: Export"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        export_info = context.scene.mkwctt_export_info

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.operator('scene.mkwctt_export', icon='EXPORT')

        layout.separator(factor=2.)

        layout.label(text="Settings", icon='PREFERENCES')
        layout.prop(export_info, 'scale')
