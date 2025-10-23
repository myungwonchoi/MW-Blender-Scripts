import bpy

class WM_OT_myOp(bpy.types.Operator):
    """Open the Simple Dialog box"""
    bl_label = "Simple Dialog Box"
    bl_idname = "wm.myop"
    
    text : bpy.props.StringProperty(name="Enter Text", default="")
    number : bpy.props.FloatProperty(name="Scale Z Axis", default=1)
    
    def execute(self, context):
        
        t = self.text
        n = self.number
        
        # 여기에 실행할 작업을 넣으세요
        print(f"입력된 텍스트: {t}")
        print(f"입력된 숫자: {n}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "text")
        layout.prop(self, "number")

def register():
    bpy.utils.register_class(WM_OT_myOp)

def unregister():
    bpy.utils.unregister_class(WM_OT_myOp)

if __name__ == "__main__":
    register()

    bpy.ops.wm.myop('INVOKE_DEFAULT')