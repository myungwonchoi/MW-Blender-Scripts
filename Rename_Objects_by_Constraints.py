import bpy

def get_constraint_targets(obj):
    """
    주어진 오브젝트의 컨스트레인트 타겟들을 찾아 반환하는 함수
    """
    targets = set()
    
    # 오브젝트 레벨 컨스트레인트 확인
    if hasattr(obj, 'constraints'):
        for constraint in obj.constraints:
            # 컨스트레인트의 타겟 오브젝트 확인
            if hasattr(constraint, 'target') and constraint.target:
                targets.add(constraint.target)
    
    # Pose 본의 컨스트레인트도 확인 (아마추어인 경우)
    if obj.type == 'ARMATURE' and obj.pose:
        for pose_bone in obj.pose.bones:
            for constraint in pose_bone.constraints:
                if hasattr(constraint, 'target') and constraint.target:
                    targets.add(constraint.target)
    
    return targets

def rename_objects_by_constraints():
    """
    선택된 오브젝트들의 이름을 연결된 컨스트레인트 타겟 오브젝트 이름을 기반으로 변경하는 함수
    이름 형식: "CTRL_" + 연결된 오브젝트의 이름
    """
    
    # 현재 선택된 오브젝트들 가져오기
    selected_objects = list(bpy.context.selected_objects)
    
    if not selected_objects:
        print("선택된 오브젝트가 없습니다.")
        return {'CANCELLED'}
    
    renamed_count = 0
    
    for obj in selected_objects:
        # 현재 오브젝트의 컨스트레인트 타겟들 찾기
        targets = get_constraint_targets(obj)
        
        if not targets:
            print(f"'{obj.name}' 오브젝트에 컨스트레인트 타겟이 없습니다.")
            continue
        
        # 여러 타겟이 있는 경우 첫 번째 타겟 사용
        target = list(targets)[0]
        
        # 새로운 이름 생성
        new_name = f"CTRL_{target.name}"
        
        # 기존 이름 저장
        old_name = obj.name
        
        # 이름 변경
        try:
            obj.name = new_name
            renamed_count += 1
            print(f"'{old_name}' -> '{obj.name}' (타겟: {target.name})")
            
            # 여러 타겟이 있는 경우 알림
            if len(targets) > 1:
                target_names = [t.name for t in targets]
                print(f"  주의: 여러 타겟이 발견되었습니다: {target_names}")
                print(f"  첫 번째 타겟 '{target.name}'을 사용했습니다.")
                
        except Exception as e:
            print(f"'{obj.name}' 이름 변경 실패: {str(e)}")
    
    if renamed_count > 0:
        print(f"총 {renamed_count}개의 오브젝트 이름이 변경되었습니다.")
    else:
        print("변경된 오브젝트가 없습니다.")
    
    return {'FINISHED'}

def rename_objects_by_specific_constraint_type(constraint_type=None):
    """
    특정 컨스트레인트 타입만을 기준으로 오브젝트 이름을 변경하는 함수
    constraint_type: 'COPY_LOCATION', 'COPY_ROTATION', 'TRACK_TO' 등
    """
    
    selected_objects = list(bpy.context.selected_objects)
    
    if not selected_objects:
        print("선택된 오브젝트가 없습니다.")
        return {'CANCELLED'}
    
    renamed_count = 0
    
    for obj in selected_objects:
        target_found = None
        
        # 오브젝트 레벨 컨스트레인트 확인
        if hasattr(obj, 'constraints'):
            for constraint in obj.constraints:
                # 특정 타입의 컨스트레인트만 확인 (타입 지정된 경우)
                if constraint_type and constraint.type != constraint_type:
                    continue
                
                if hasattr(constraint, 'target') and constraint.target:
                    target_found = constraint.target
                    break
        
        # Pose 본의 컨스트레인트도 확인 (아마추어인 경우)
        if not target_found and obj.type == 'ARMATURE' and obj.pose:
            for pose_bone in obj.pose.bones:
                for constraint in pose_bone.constraints:
                    # 특정 타입의 컨스트레인트만 확인 (타입 지정된 경우)
                    if constraint_type and constraint.type != constraint_type:
                        continue
                        
                    if hasattr(constraint, 'target') and constraint.target:
                        target_found = constraint.target
                        break
                if target_found:
                    break
        
        if not target_found:
            type_msg = f" (타입: {constraint_type})" if constraint_type else ""
            print(f"'{obj.name}' 오브젝트에 해당하는 컨스트레인트 타겟이 없습니다.{type_msg}")
            continue
        
        # 새로운 이름 생성
        new_name = f"CTRL_{target_found.name}"
        
        # 기존 이름 저장
        old_name = obj.name
        
        # 이름 변경
        try:
            obj.name = new_name
            renamed_count += 1
            constraint_info = f" ({constraint_type})" if constraint_type else ""
            print(f"'{old_name}' -> '{obj.name}' (타겟: {target_found.name}){constraint_info}")
                
        except Exception as e:
            print(f"'{obj.name}' 이름 변경 실패: {str(e)}")
    
    if renamed_count > 0:
        print(f"총 {renamed_count}개의 오브젝트 이름이 변경되었습니다.")
    else:
        print("변경된 오브젝트가 없습니다.")
    
    return {'FINISHED'}

# 메인 실행 부분
if __name__ == "__main__":
    # 기본 실행: 모든 컨스트레인트 타입 고려
    rename_objects_by_constraints()
    
    # 특정 컨스트레인트 타입만 고려하려면 아래와 같이 사용:
    # rename_objects_by_specific_constraint_type('COPY_LOCATION')
    # rename_objects_by_specific_constraint_type('COPY_ROTATION')
    # rename_objects_by_specific_constraint_type('TRACK_TO')