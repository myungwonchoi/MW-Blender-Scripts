import bpy

def get_constraint_related_objects(start_objects):
    """
    주어진 오브젝트들과 컨스트레인트 관계를 가진 모든 오브젝트를 찾아 반환하는 함수
    """
    related_objects = set()
    objects_to_check = set(start_objects)
    processed_objects = set()
    
    while objects_to_check:
        current_obj = objects_to_check.pop()
        
        if current_obj in processed_objects:
            continue
            
        processed_objects.add(current_obj)
        related_objects.add(current_obj)
        
        # 현재 오브젝트의 모든 컨스트레인트 확인
        if hasattr(current_obj, 'constraints'):
            for constraint in current_obj.constraints:
                # 컨스트레인트의 타겟 오브젝트 확인
                if hasattr(constraint, 'target') and constraint.target:
                    target = constraint.target
                    if target not in processed_objects:
                        objects_to_check.add(target)
                
                # 서브타겟이 있는 경우 (예: Track To 컨스트레인트)
                if hasattr(constraint, 'subtarget') and constraint.subtarget:
                    if constraint.target and constraint.target.type == 'ARMATURE':
                        # 아마추어의 본을 참조하는 경우, 아마추어 오브젝트 자체를 추가
                        if constraint.target not in processed_objects:
                            objects_to_check.add(constraint.target)
        
        # Pose 본의 컨스트레인트도 확인 (아마추어인 경우)
        if current_obj.type == 'ARMATURE' and current_obj.pose:
            for pose_bone in current_obj.pose.bones:
                for constraint in pose_bone.constraints:
                    if hasattr(constraint, 'target') and constraint.target:
                        target = constraint.target
                        if target not in processed_objects:
                            objects_to_check.add(target)
        
        # 현재 오브젝트를 타겟으로 하는 다른 오브젝트들의 컨스트레인트 확인
        for obj in bpy.data.objects:
            if obj in processed_objects:
                continue
                
            # 오브젝트 레벨 컨스트레인트 확인
            if hasattr(obj, 'constraints'):
                for constraint in obj.constraints:
                    if hasattr(constraint, 'target') and constraint.target == current_obj:
                        if obj not in processed_objects:
                            objects_to_check.add(obj)
            
            # Pose 본 컨스트레인트 확인
            if obj.type == 'ARMATURE' and obj.pose:
                for pose_bone in obj.pose.bones:
                    for constraint in pose_bone.constraints:
                        if hasattr(constraint, 'target') and constraint.target == current_obj:
                            if obj not in processed_objects:
                                objects_to_check.add(obj)
    
    return related_objects

def select_constraint_related_objects():
    """
    선택된 오브젝트와 서로 컨스트레인트 관계를 가진 모든 오브젝트를 선택하는 함수
    """
    
    # 현재 선택된 오브젝트들 가져오기
    initially_selected = list(bpy.context.selected_objects)
    
    if not initially_selected:
        print("선택된 오브젝트가 없습니다.")
        return {'CANCELLED'}
    
    print(f"시작 오브젝트: {[obj.name for obj in initially_selected]}")
    
    # 컨스트레인트 관련 오브젝트들 찾기
    related_objects = get_constraint_related_objects(initially_selected)
    
    # 모든 오브젝트 선택 해제
    bpy.ops.object.select_all(action='DESELECT')
    
    # 관련 오브젝트들 선택
    selected_count = 0
    for obj in related_objects:
        try:
            obj.select_set(True)
            selected_count += 1
            print(f"선택됨: {obj.name}")
        except:
            print(f"선택 실패: {obj.name}")
    
    # 새롭게 발견된 관련 오브젝트 중 하나를 활성 오브젝트로 설정
    # 기존에 선택되었던 오브젝트들을 제외한 새로운 오브젝트들 찾기
    newly_found_objects = related_objects - set(initially_selected)
    
    active_obj = None
    # 새롭게 발견된 오브젝트가 있다면 그 중 하나를 활성화
    if newly_found_objects:
        active_obj = next(iter(newly_found_objects))
        print(f"새롭게 발견된 관련 오브젝트: {[obj.name for obj in newly_found_objects]}")
    # 새로운 오브젝트가 없다면 기존 오브젝트 중 첫 번째를 활성화
    elif initially_selected and initially_selected[0] in related_objects:
        active_obj = initially_selected[0]
    
    # 활성 오브젝트 설정
    if active_obj:
        bpy.context.view_layer.objects.active = active_obj
        print(f"활성 오브젝트: {active_obj.name}")
    
    print(f"총 {selected_count}개의 관련 오브젝트가 선택되고 활성화되었습니다.")
    return {'FINISHED'}

# 메인 실행 부분
if __name__ == "__main__":
    select_constraint_related_objects()