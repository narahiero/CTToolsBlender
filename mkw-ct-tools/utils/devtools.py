
import shutil

import bpy


ADDON_NAME = __package__.split('.')[0]


class MKWCTT_dev_settings(bpy.types.AddonPreferences):
    """Development tools settings"""
    bl_idname = ADDON_NAME

    srcdir: bpy.props.StringProperty(
        name="Source directory",
        subtype='DIR_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'srcdir')


class MKWCTT_OT_reload_addon(bpy.types.Operator):
    """Development tool to update addon sources and reload scripts"""
    bl_idname = 'mkwctt.reload_addon'
    bl_label = "Reload MKW CT Tools"

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[ADDON_NAME].preferences
        addon_dir = bpy.utils.user_resource('SCRIPTS', path="addons/"+ADDON_NAME)

        shutil.rmtree(addon_dir)
        shutil.copytree(addon_prefs.srcdir, addon_dir)

        bpy.ops.script.reload()

        return {'FINISHED'}
