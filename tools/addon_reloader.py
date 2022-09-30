
bl_info = {
    "name": "Add-on Reloader",
    "description": "Development tool to update add-on sources and reload scripts",
    "author": "Nara Hiero",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "support": "COMMUNITY",
    "category": "Development",
}


import os
import shutil

import bpy


class AddonReloaderSettings(bpy.types.AddonPreferences):
    """Settings"""
    bl_idname = __name__

    addontype: bpy.props.EnumProperty(
        name="Add-on Type",
        description="The type of Python program of your add-on",
        default='script',
        items=[
            ('script', "Script", "The add-on code is contained within a single source file", 'TEXT', 0),
            ('module', "Module", "The add-on is a module comprised of multiple source files", 'DOCUMENTS', 1)
        ])

    srcfile: bpy.props.StringProperty(
        name="Script path",
        subtype='FILE_PATH',
    )

    srcdir: bpy.props.StringProperty(
        name="Module directory",
        subtype='DIR_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'addontype')
        if self.addontype == 'script':
            layout.prop(self, 'srcfile')
        else:
            layout.prop(self, 'srcdir')


class SCRIPT_OT_reload_addon(bpy.types.Operator):
    """Development tool to update add-on sources and reload scripts"""
    bl_idname = 'script.reload_addon'
    bl_label = "Reload Add-on"

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        if addon_prefs.addontype == 'script':
            addon_src = addon_prefs.srcfile
            if not os.path.isfile(addon_src):
                return {'FINISHED'}
        else:
            addon_src: str = addon_prefs.srcdir
            if not os.path.isdir(addon_src):
                return {'FINISHED'}

            while addon_src.endswith('/') or addon_src.endswith('\\'):
                addon_src = addon_src[:-1]

        if addon_src == "":
            return {'FINISHED'}

        addon_name = os.path.basename(addon_src)
        addon_path = bpy.utils.user_resource('SCRIPTS', path="addons/"+addon_name)

        if addon_prefs.addontype == 'script':
            if os.path.isfile(addon_path):
                os.remove(addon_path)
            shutil.copyfile(addon_prefs.srcfile, addon_path)
        else:
            if os.path.isdir(addon_path):
                shutil.rmtree(addon_path)
            shutil.copytree(addon_prefs.srcdir, addon_path)

        bpy.ops.script.reload()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(AddonReloaderSettings)
    bpy.utils.register_class(SCRIPT_OT_reload_addon)

def unregister():
    bpy.utils.unregister_class(SCRIPT_OT_reload_addon)
    bpy.utils.unregister_class(AddonReloaderSettings)
