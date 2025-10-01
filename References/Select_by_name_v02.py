bl_info = {
    "name": "Select by Name",
    "blender": (3, 0, 0),
    "category": "Animation",
    "author": "HungLe93",
    "version": (1, 0),
    "location": "Object Mode > Select > Select by name Or Pose Mode > Pose > Select by name ",
    "description": "Select object or bone by name. Press F5 and fill name.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
}


import bpy

# == OPERATORS
class OBJECT_OT_select_by_name(bpy.types.Operator):
    bl_idname = "object.select_by_name"
    bl_label = "Select by Name"
    bl_property = "object_enum"

    filter_string: bpy.props.StringProperty(name="Filter String", description="Enter search string to filter items")
    
    def get_items(self, context):
        items = []
        filter_string_lower = self.filter_string.lower()
        
        if context.mode == 'POSE':
            # Check if in Pose mode, then find bones
            armature = context.active_object
            if armature and armature.type == 'ARMATURE':
                for bone in armature.pose.bones:
                    if filter_string_lower in bone.name.lower():
                        items.append((bone.name, bone.name, ""))
        
        else:
            # Default to searching objects
            for obj in bpy.data.objects:
                if filter_string_lower in obj.name.lower():
                    items.append((obj.name, obj.name, ""))
        
        if not items:
            items.append(("NONE", "No items found", ""))
        return items

    object_enum: bpy.props.EnumProperty(items=get_items, name='Name', description="Filtered items")

    def execute(self, context):
        if context.mode == 'POSE':
            # Select bone in Pose mode
            armature = context.active_object
            if armature and armature.type == 'ARMATURE':
                bone = armature.pose.bones.get(self.object_enum)
                if bone:
                    bpy.ops.pose.select_all(action='DESELECT')
                    bone.bone.select = True
                    context.view_layer.objects.active = armature
                    self.report({'INFO'}, f"Selected bone: {bone.name}")
                else:
                    self.report({'ERROR'}, f"Bone '{self.object_enum}' not found in active armature")
            else:
                self.report({'ERROR'}, "No active armature in Pose mode")
        
        else:
            # Select object in Object mode
            obj = bpy.data.objects.get(self.object_enum)
            if obj:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                self.report({'INFO'}, f"Selected object: {obj.name}")
            else:
                self.report({'ERROR'}, f"Object '{self.object_enum}' not found in scene")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filter_string = ""
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "filter_string", text="Filter")
        layout.prop(self, "object_enum", text="Item")

# == MAIN ROUTINE
CLASSES = [
    OBJECT_OT_select_by_name,
]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    # Add operator to the Select menu in the 3D Viewport for both Object Mode and Pose Mode
    bpy.types.VIEW3D_MT_select_object.append(menu_func)
    bpy.types.VIEW3D_MT_pose.append(menu_func)

    # Add keymap entry for F5
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new('object.select_by_name', 'F5', 'PRESS')
    addon_keymaps.append((km, kmi))

def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    # Remove from the Select menu in the 3D Viewport
    bpy.types.VIEW3D_MT_select_object.remove(menu_func)
    bpy.types.VIEW3D_MT_pose.remove(menu_func)

    # Remove keymap entry for F5
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

addon_keymaps = []

def menu_func(self, context):
    layout = self.layout
    layout.operator("object.select_by_name", text="Select by name")

if __name__ == '__main__':
    register()
