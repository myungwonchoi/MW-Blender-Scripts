import bpy
import bmesh
from mathutils import Vector

def add_following_bone_to_armature():
    """
    선택된 아마추어와 여러 오브젝트를 기반으로 새로운 본들을 생성하고
    Copy Transforms 콘스트레인트를 추가하는 함수
    """
    
    # 선택된 오브젝트 가져오기
    selected_objects = bpy.context.selected_objects
    
    if len(selected_objects) < 2:
        print("최소 2개의 오브젝트를 선택해주세요 (아마추어 + 타겟 오브젝트들)")
        return {'CANCELLED'}
    
    # 아마추어와 타겟 오브젝트들 구분
    armature_obj = None
    target_objects = []
    
    for obj in selected_objects:
        if obj.type == 'ARMATURE':
            if armature_obj is None:
                armature_obj = obj
            else:
                print("아마추어는 하나만 선택해주세요.")
                return {'CANCELLED'}
        else:
            target_objects.append(obj)
    
    if armature_obj is None:
        print("선택된 오브젝트 중 아마추어가 없습니다.")
        return {'CANCELLED'}
    
    if not target_objects:
        print("타겟 오브젝트를 최소 하나 이상 선택해주세요.")
        return {'CANCELLED'}
    
    # 아마추어를 액티브 오브젝트로 설정
    bpy.context.view_layer.objects.active = armature_obj
    
    # Edit 모드로 전환
    bpy.ops.object.mode_set(mode='EDIT')
    
    # 각 타겟 오브젝트별로 새로운 본 생성
    armature_data = armature_obj.data
    created_bones = []
    
    for target_obj in target_objects:
        # 새로운 본 생성
        new_bone = armature_data.edit_bones.new(target_obj.name)
        
        # 타겟 오브젝트의 위치를 기준으로 본 위치 설정
        target_location = target_obj.location
        new_bone.head = target_location
        new_bone.tail = target_location + Vector((0, 0, 1))  # Z축으로 1유닛 연장
        
        created_bones.append(target_obj.name)
        print(f"본 '{target_obj.name}'이 생성되었습니다.")
    
    # Pose 모드로 전환
    bpy.ops.object.mode_set(mode='POSE')
    
    # 각 새로 생성된 본에 Copy Transforms 콘스트레인트 추가
    for i, target_obj in enumerate(target_objects):
        bone_name = created_bones[i]
        pose_bone = armature_obj.pose.bones[bone_name]
        
        # Copy Transforms 콘스트레인트 추가
        constraint = pose_bone.constraints.new(type='COPY_TRANSFORMS')
        constraint.name = "Copy Transforms"
        constraint.target = target_obj
        
        print(f"Copy Transforms 콘스트레인트가 본 '{bone_name}'에 타겟 '{target_obj.name}'으로 설정되었습니다.")
    
    # Object 모드로 되돌아가기
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"총 {len(target_objects)}개의 본이 아마추어 '{armature_obj.name}'에 생성되었습니다.")
    
    return {'FINISHED'}

# 메인 실행 부분
if __name__ == "__main__":
    add_following_bone_to_armature()