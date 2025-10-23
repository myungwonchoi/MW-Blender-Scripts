import bpy

class WM_OT_ActionSelector(bpy.types.Operator):
    """Open the Action Selector Dialog box"""
    bl_label = "Action Selector Dialog"
    bl_idname = "wm.action_selector"
    
    # 모든 액션을 불러오는 EnumProperty
    def get_actions(self, context):
        actions = []
        
        # 씬에 있는 모든 액션 수집
        for action in bpy.data.actions:
            actions.append((action.name, action.name, f"Action: {action.name}"))
        
        # 액션이 없으면 기본 아이템 추가
        if not actions:
            actions.append(('NONE', 'No Actions', 'No actions available'))
        
        return actions
    
    selected_action : bpy.props.EnumProperty(
        name="Select Action",
        description="Choose an action from the list",
        items=get_actions
    )
    
    def execute(self, context):
        
        action_name = self.selected_action
        
        # 선택된 액션 출력
        print(f"선택된 액션: {action_name}")
        
        # 선택된 액션이 있고 'NONE'이 아닌 경우
        if action_name != 'NONE' and action_name in bpy.data.actions:
            selected_action = bpy.data.actions[action_name]
            print(f"액션 정보:")
            print(f"  - 이름: {selected_action.name}")
            print(f"  - 프레임 범위: {selected_action.frame_range}")
            print(f"  - FCurve 개수: {len(selected_action.fcurves)}")
            
            # 선택된 모든 오브젝트에 액션 적용
            selected_objects = context.selected_objects
            applied_count = 0
            
            for obj in selected_objects:
                # 모든 오브젝트 타입 처리 (MESH, ARMATURE, CAMERA, LIGHT 등)
                try:
                    # 애니메이션 데이터가 없으면 생성
                    if not obj.animation_data:
                        obj.animation_data_create()
                    
                    # 액션 적용
                    obj.animation_data.action = selected_action
                    applied_count += 1
                    print(f"액션 '{action_name}'을 {obj.name} ({obj.type})에 적용했습니다.")
                    
                except Exception as e:
                    print(f"오브젝트 '{obj.name}' ({obj.type})에 액션 적용 실패: {e}")
            
            if applied_count > 0:
                print(f"총 {applied_count}개의 오브젝트에 액션을 적용했습니다.")
                self.report({'INFO'}, f"액션 '{action_name}'을 {applied_count}개 오브젝트에 적용했습니다.")
            else:
                print("선택된 오브젝트가 없거나 액션 적용에 실패했습니다.")
                self.report({'WARNING'}, "선택된 오브젝트가 없거나 액션 적용에 실패했습니다.")
        else:
            self.report({'ERROR'}, "유효한 액션이 선택되지 않았습니다.")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        # 액션 선택 메뉴
        layout.label(text="Choose Action to Apply:", icon='ACTION')
        layout.prop(self, "selected_action")
        
        layout.separator()
        
        # 선택된 오브젝트들 정보
        selected_objects = context.selected_objects
        
        layout.label(text=f"Selected Objects: {len(selected_objects)}")
        
        if selected_objects:
            layout.separator()
            layout.label(text="Target Objects:")
            # 최대 5개까지만 표시
            for i, obj in enumerate(selected_objects[:5]):
                current_action = "None"
                if obj.animation_data and obj.animation_data.action:
                    current_action = obj.animation_data.action.name
                layout.label(text=f"  • {obj.name} ({obj.type}) - Action: {current_action}")
            
            # 5개 이상이면 "..." 표시
            if len(selected_objects) > 5:
                layout.label(text=f"  • ... and {len(selected_objects) - 5} more objects")
        else:
            layout.separator()
            layout.label(text="No objects selected!", icon='ERROR')

def register():
    bpy.utils.register_class(WM_OT_ActionSelector)

def unregister():
    bpy.utils.unregister_class(WM_OT_ActionSelector)

if __name__ == "__main__":
    register()
    
    # 테스트용으로 다이얼로그 실행
    bpy.ops.wm.action_selector('INVOKE_DEFAULT')