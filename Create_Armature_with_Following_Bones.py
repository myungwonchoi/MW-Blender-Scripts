import bpy
import bmesh
from mathutils import Vector

def create_armature_with_following_bones():
    """
    선택된 오브젝트들을 기반으로 새로운 아마추어를 생성하고
    각 오브젝트를 따라가는 본들을 생성한 후 Copy Transforms 콘스트레인트를 추가하는 함수
    """
    
    # 선택된 오브젝트 가져오기
    selected_objects = bpy.context.selected_objects
    
    if not selected_objects:
        print("최소 1개의 오브젝트를 선택해주세요.")
        return {'CANCELLED'}
    
    # 아마추어는 제외하고 타겟 오브젝트들만 필터링
    target_objects = []
    for obj in selected_objects:
        if obj.type != 'ARMATURE':
            target_objects.append(obj)
    
    if not target_objects:
        print("아마추어가 아닌 오브젝트를 최소 하나 이상 선택해주세요.")
        return {'CANCELLED'}
    
    print(f"{len(target_objects)}개의 타겟 오브젝트를 찾았습니다: {[obj.name for obj in target_objects]}")
    
    # 새로운 아마추어 생성
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
    armature_obj = bpy.context.active_object
    
    # 아마추어 이름 설정 (첫 번째 타겟 오브젝트 이름 기반)
    if len(target_objects) == 1:
        armature_obj.name = f"{target_objects[0].name}_Armature"
    else:
        armature_obj.name = f"Following_Armature"
    
    print(f"새로운 아마추어 '{armature_obj.name}'이 생성되었습니다.")
    
    # 기본 본 삭제 (자동 생성된 "Bone" 삭제)
    bpy.ops.object.mode_set(mode='EDIT')
    armature_data = armature_obj.data
    
    # 기존 본들 삭제
    for bone in list(armature_data.edit_bones):
        armature_data.edit_bones.remove(bone)
    
    # 각 타겟 오브젝트별로 새로운 본 생성
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
    
    # 생성된 아마추어와 모든 타겟 오브젝트들을 선택
    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    for target_obj in target_objects:
        target_obj.select_set(True)
    
    # 아마추어를 액티브로 설정
    bpy.context.view_layer.objects.active = armature_obj
    
    print(f"총 {len(target_objects)}개의 본이 새로운 아마추어 '{armature_obj.name}'에 생성되었습니다.")
    print("생성된 아마추어와 모든 타겟 오브젝트들이 선택되었습니다.")
    
    return {'FINISHED'}

# 메인 실행 부분
if __name__ == "__main__":
    print("=" * 60)
    print("오브젝트 기반 아마추어 + Following Bones 생성 스크립트")
    print("=" * 60)
    
    # 선택된 오브젝트 정보 출력
    selected = bpy.context.selected_objects
    
    if selected:
        print(f"선택된 오브젝트: {len(selected)}개")
        target_objects = [obj for obj in selected if obj.type != 'ARMATURE']
        armature_objects = [obj for obj in selected if obj.type == 'ARMATURE']
        
        print(f"타겟 오브젝트: {len(target_objects)}개")
        for obj in target_objects:
            print(f"  - {obj.name} ({obj.type})")
        
        if armature_objects:
            print(f"아마추어 오브젝트: {len(armature_objects)}개 (무시됨)")
            for obj in armature_objects:
                print(f"  - {obj.name} (무시)")
        
        print(f"\n새로운 아마추어를 생성하고 {len(target_objects)}개의 Following Bones를 추가합니다...")
        result = create_armature_with_following_bones()
        
    else:
        print("오브젝트를 선택하지 않았습니다.")
        print("사용법: 원하는 오브젝트들을 선택한 후 스크립트를 실행하세요.")
        result = {'CANCELLED'}
    
    print(f"\n실행 결과: {result}")