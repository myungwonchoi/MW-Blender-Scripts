"""
선택된 아마추어를 언리얼 엔진에 맞게 변환하는 스크립트입니다.

1. 아마추어와 하위 메시를 같은 콜렉션에 복사
2. Pose 기반으로 Bake Action
3. 아마추어 이름을 Root로 변경하고 100배 스케일
4. Apply Scale 적용
5. Location 키프레임에 100배 곱하기
6. Unit Scale을 0.01로 변경하고 FBX 익스포트 다이얼로그 열기
7. 종료
8. Unit Scale을 원래 값으로 수동 복원 필요
"""

import bpy
import bmesh
from mathutils import Vector

def get_all_fcurves(action):
    """
    Blender 5.0+ 호환성을 위한 F-Curve 가져오기 헬퍼 함수
    Action.fcurves (Legacy) 또는 Action.slots -> channelbag (New)를 모두 지원
    """
    # 1. Legacy API (Blender 4.x 이하)
    if hasattr(action, "fcurves"):
        return action.fcurves
    
    # 2. New API (Blender 5.0+ Slotted Actions)
    fcurves = []
    if hasattr(action, "slots"):
        try:
            from bpy_extras import anim_utils
            for slot in action.slots:
                channelbag = anim_utils.action_get_channelbag_for_slot(action, slot)
                if channelbag:
                    fcurves.extend(channelbag.fcurves)
        except ImportError:
            pass
            
    return fcurves

def convert_armature_for_unreal():
    # 현재 선택된 오브젝트들 확인
    selected_objects = list(bpy.context.selected_objects)
    
    if not selected_objects:
        print("선택된 오브젝트가 없습니다.")
        return {'CANCELLED'}
    
    # 선택된 오브젝트들 중에서 아마추어 찾기
    armature_obj = None
    armatures_found = []
    
    for obj in selected_objects:
        if obj.type == 'ARMATURE':
            armatures_found.append(obj)
    
    # 아마추어가 없으면 취소
    if not armatures_found:
        print("선택된 오브젝트들 중 아마추어가 없습니다.")
        return {'CANCELLED'}
    
    # 아마추어가 여러 개면 첫 번째 것 사용
    if len(armatures_found) > 1:
        print(f"여러 개의 아마추어가 선택되었습니다. 첫 번째 아마추어 '{armatures_found[0].name}'를 사용합니다.")
        for i, arm in enumerate(armatures_found):
            print(f"  {i+1}. {arm.name}")
    
    armature_obj = armatures_found[0]
    print(f"변환할 아마추어: {armature_obj.name}")
    
    # 1. 아마추어와 하위 메시들을 같은 콜렉션에 복사
    original_collection = None
    for collection in bpy.data.collections:
        if armature_obj.name in collection.objects:
            original_collection = collection
            break
    
    if not original_collection:
        original_collection = bpy.context.scene.collection
    
    # 복사할 오브젝트들 수집 (아마추어와 연결된 모든 메시들)
    objects_to_copy = [armature_obj]
    
    # 아마추어와 연결된 모든 메시 찾기 (부모 관계, 아마추어 모디파이어, 버텍스 그룹 등)
    connected_meshes = []
    
    for obj in bpy.context.view_layer.objects:
        if obj.type == 'MESH':
            is_connected = False
            
            # 1. 직접 부모 관계 확인
            if obj.parent == armature_obj:
                is_connected = True
                print(f"부모 관계로 연결된 메시: {obj.name}")
            
            # 2. 아마추어 모디파이어 확인
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == armature_obj:
                    is_connected = True
                    print(f"아마추어 모디파이어로 연결된 메시: {obj.name}")
                    break
            
            # 3. 버텍스 그룹이 아마추어의 본 이름과 일치하는지 확인
            if not is_connected:
                armature_bone_names = set(bone.name for bone in armature_obj.data.bones)
                mesh_vertex_groups = set(vg.name for vg in obj.vertex_groups)
                if armature_bone_names.intersection(mesh_vertex_groups):
                    is_connected = True
                    print(f"버텍스 그룹으로 연결된 메시: {obj.name}")
            
            if is_connected:
                connected_meshes.append(obj)
    
    objects_to_copy.extend(connected_meshes)
    
    print(f"복사할 오브젝트들: {[obj.name for obj in objects_to_copy]}")
    
    # 오브젝트들 복사
    copied_objects = []
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in objects_to_copy:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.duplicate()
    
    # 복사된 오브젝트들 가져오기
    copied_objects = list(bpy.context.selected_objects)
    copied_armature = None
    
    for obj in copied_objects:
        if obj.type == 'ARMATURE':
            copied_armature = obj
            break
    
    if not copied_armature:
        print("아마추어 복사에 실패했습니다.")
        return {'CANCELLED'}
    
    print(f"복사된 아마추어: {copied_armature.name}")

    
    # 2. Pose 기반 Bake Action으로 컨스트레인트 제거
    bpy.context.view_layer.objects.active = copied_armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # 모든 pose bone 선택
    bpy.ops.pose.select_all(action='SELECT')
    
    # 씬의 프레임 범위를 기준으로 베이크 진행
    scene = bpy.context.scene
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    
    # 무조건 베이크 진행 - 씬의 프레임 범위 사용
    bpy.ops.nla.bake(
        frame_start=frame_start,
        frame_end=frame_end,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        clear_parents=False,
        use_current_action=True,
        bake_types={'POSE'}
    )
    print(f"Pose 기반 Bake Action 완료 (프레임 {frame_start}-{frame_end})")
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 3. 아마추어 이름을 Root로 변  경하고 100배 스케일
    copied_armature.name = "Armature"
    copied_armature.scale = (100, 100, 100)
    
    print("아마추어 이름을 Root로 변경하고 100배 스케일 적용")

    # 4. Apply Scale 적용
    # 모든 복사된 오브젝트 선택
    bpy.ops.object.select_all(action='DESELECT')
    for obj in copied_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = copied_armature # 아마추어를 활성 오브젝트로 설정

    # Apply Scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print("Apply Scale 적용 완료")
    
    # 5. Location 키프레임에 100배 곱하기
    if copied_armature.animation_data and copied_armature.animation_data.action:
        action = copied_armature.animation_data.action
        location_curves_updated = 0
        
        for fcurve in get_all_fcurves(action):
            if fcurve.data_path.endswith('location'):
                for keyframe in fcurve.keyframe_points:
                    keyframe.co.y *= 100
                    keyframe.handle_left.y *= 100
                    keyframe.handle_right.y *= 100
                location_curves_updated += 1
        
        print(f"Location 키프레임 {location_curves_updated}개 곡선에 100배 적용")
    
    # 6. 새로운 Empty 생성 및 페어런트 (Unit Scale 변경 대신)
    empty = bpy.data.objects.new(f"Empty_UE_Armature", None)
    if copied_armature.users_collection:
        copied_armature.users_collection[0].objects.link(empty)
    else:
        bpy.context.collection.objects.link(empty)
    
    empty.scale = (0.01, 0.01, 0.01)
    
    # 아마추어를 Empty에 페어런트
    copied_armature.parent = empty
    
    # 메시들도 확인하여 페어런트 (아마추어의 자식이 아닌 경우)
    for obj in copied_objects:
        if obj.type == 'MESH' and obj.parent != copied_armature:
            obj.parent = empty
    
    print("Empty 생성 및 페어런트 완료 (시각적 크기 복원)")

    # 최종 선택 상태 설정 - 스켈레탈 메시와 하위 메시들을 모두 선택
    bpy.ops.object.select_all(action='DESELECT')
    
    # 변환된 아마추어와 연결된 모든 메시들 선택
    copied_armature.select_set(True)
    for obj in copied_objects:
        if obj.type == 'MESH':
            obj.select_set(True)
    
    bpy.context.view_layer.objects.active = copied_armature

    return {'FINISHED'}

# 메인 실행 부분
if __name__ == "__main__":
    convert_armature_for_unreal()   