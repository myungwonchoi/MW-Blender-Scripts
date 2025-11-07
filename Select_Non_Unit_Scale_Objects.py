"""
Select Non-Unit Scale Objects
선택한 오브젝트 중에서 Scale 값이 1 1 1이 아닌 오브젝트만 다시 선택하는 스크립트
"""

import bpy
from bpy.types import Operator


class MW_OT_SelectNonUnitScale(Operator):
    """Select objects with non-unit scale (not 1,1,1)"""
    bl_idname = "mw.select_non_unit_scale"
    bl_label = "Select Non-Unit Scale Objects"
    bl_description = "Select objects from current selection that don't have scale 1,1,1"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 현재 선택된 오브젝트들 저장
        currently_selected = list(context.selected_objects)
        
        if not currently_selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        # 모든 선택 해제
        bpy.ops.object.select_all(action='DESELECT')
        
        # Scale이 1,1,1이 아닌 오브젝트 찾기
        non_unit_scale_objects = []
        
        for obj in currently_selected:
            scale = obj.scale
            # 부동소수점 비교를 위해 작은 허용 오차 사용
            tolerance = 0.0001
            
            if (abs(scale.x - 1.0) > tolerance or 
                abs(scale.y - 1.0) > tolerance or 
                abs(scale.z - 1.0) > tolerance):
                
                non_unit_scale_objects.append(obj)
                obj.select_set(True)
        
        # 결과 보고
        total_selected = len(currently_selected)
        non_unit_count = len(non_unit_scale_objects)
        
        if non_unit_count > 0:
            # 마지막으로 선택된 오브젝트를 active로 설정
            context.view_layer.objects.active = non_unit_scale_objects[-1]
            
            self.report({'INFO'}, 
                f"Selected {non_unit_count} objects with non-unit scale out of {total_selected} total objects")
            
            # 각 오브젝트의 scale 값 출력
            print(f"\n=== Non-Unit Scale Objects ===")
            for obj in non_unit_scale_objects:
                scale = obj.scale
                print(f"{obj.name}: Scale({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f})")
        else:
            self.report({'INFO'}, 
                f"All {total_selected} selected objects have unit scale (1,1,1)")
        
        return {'FINISHED'}


# 등록/해제 함수
def register():
    bpy.utils.register_class(MW_OT_SelectNonUnitScale)


def unregister():
    bpy.utils.unregister_class(MW_OT_SelectNonUnitScale)


# 메인 실행부
if __name__ == "__main__":
    # 기존 등록 해제 (안전성)
    try:
        unregister()
    except:
        pass
    
    # 클래스 등록
    register()
    
    # 현재 선택된 오브젝트 정보 출력
    selected_objects = bpy.context.selected_objects
    print(f"\n=== MW Select Non-Unit Scale Objects ===")
    print(f"Currently selected objects: {len(selected_objects)}")
    
    if selected_objects:
        print("Selected objects and their scales:")
        for obj in selected_objects:
            scale = obj.scale
            print(f"  {obj.name}: Scale({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f})")
        
        # 스크립트 실행
        print("\nExecuting non-unit scale selection...")
        bpy.ops.mw.select_non_unit_scale()
    else:
        print("No objects selected. Please select some objects first.")
        print("Usage: Select objects -> Run this script")