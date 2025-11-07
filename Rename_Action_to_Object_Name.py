import bpy

def rename_actions_to_object_name():
    """
    선택된 오브젝트들의 액션 이름을 해당 오브젝트 이름으로 변경하는 함수
    (bpy.data.actions[""].name을 변경)
    """
    
    # 선택된 오브젝트들 가져오기
    selected_objects = bpy.context.selected_objects
    
    if not selected_objects:
        print("선택된 오브젝트가 없습니다.")
        return {'CANCELLED'}
    
    processed_count = 0
    
    for obj in selected_objects:
        print(f"\n오브젝트 '{obj.name}' 처리 중...")
        
        # 오브젝트에 애니메이션 데이터가 있는지 확인
        if not obj.animation_data:
            print(f"  - 애니메이션 데이터가 없습니다.")
            continue
        
        # 액션이 있는지 확인
        if not obj.animation_data.action:
            print(f"  - 액션이 없습니다.")
            continue
        
        action = obj.animation_data.action
        old_action_name = action.name
        
        # 액션 이름을 오브젝트 이름으로 변경
        new_action_name = obj.name
        
        # 동일한 이름의 액션이 이미 존재하는지 확인
        if new_action_name in bpy.data.actions and bpy.data.actions[new_action_name] != action:
            # 중복 방지를 위해 숫자 접미사 추가
            counter = 1
            while f"{new_action_name}.{counter:03d}" in bpy.data.actions:
                counter += 1
            new_action_name = f"{new_action_name}.{counter:03d}"
            print(f"  - 중복 방지: 액션 이름을 '{new_action_name}'로 설정")
        
        # 액션 이름 변경
        action.name = new_action_name
        
        print(f"  - 액션 이름 변경: '{old_action_name}' → '{new_action_name}'")
        processed_count += 1
    
    if processed_count > 0:
        print(f"\n총 {processed_count}개의 액션 이름이 변경되었습니다.")
        return {'FINISHED'}
    else:
        print("\n변경된 액션이 없습니다.")
        return {'CANCELLED'}

def rename_all_actions_to_object_name():
    """
    씬의 모든 오브젝트에 대해 액션 이름을 오브젝트 이름으로 변경하는 함수 (선택 여부 무관)
    """
    
    all_objects = bpy.data.objects
    processed_count = 0
    
    print("씬의 모든 오브젝트를 대상으로 액션 이름을 변경합니다...")
    
    for obj in all_objects:
        # 오브젝트에 애니메이션 데이터가 있는지 확인
        if not obj.animation_data or not obj.animation_data.action:
            continue
        
        action = obj.animation_data.action
        old_action_name = action.name
        
        # 이미 처리된 액션인지 확인 (같은 액션을 여러 오브젝트가 공유할 수 있음)
        if action.name == obj.name:
            continue  # 이미 올바른 이름
        
        # 액션 이름을 오브젝트 이름으로 변경
        new_action_name = obj.name
        
        # 동일한 이름의 액션이 이미 존재하는지 확인
        if new_action_name in bpy.data.actions and bpy.data.actions[new_action_name] != action:
            # 중복 방지를 위해 숫자 접미사 추가
            counter = 1
            while f"{new_action_name}.{counter:03d}" in bpy.data.actions:
                counter += 1
            new_action_name = f"{new_action_name}.{counter:03d}"
        
        # 액션 이름 변경
        action.name = new_action_name
        
        print(f"오브젝트 '{obj.name}': 액션 이름 '{old_action_name}' → '{new_action_name}'")
        processed_count += 1
    
    if processed_count > 0:
        print(f"\n총 {processed_count}개의 액션 이름이 변경되었습니다.")
        return {'FINISHED'}
    else:
        print("\n변경된 액션이 없습니다.")
        return {'CANCELLED'}

# 스크립트 실행
if __name__ == "__main__":
    print("=" * 60)
    print("액션 이름을 오브젝트 이름으로 변경하는 스크립트")
    print("=" * 60)
    
    # 선택된 오브젝트 정보 출력
    selected = bpy.context.selected_objects
    
    if selected:
        print(f"선택된 오브젝트: {len(selected)}개")
        for obj in selected:
            has_action = obj.animation_data and obj.animation_data.action
            action_name = obj.animation_data.action.name if has_action else "없음"
            print(f"  - {obj.name} (액션: {action_name})")
        
        print("\n선택된 오브젝트들의 액션 이름을 변경합니다...")
        result = rename_actions_to_object_name()
        
    else:
        print("선택된 오브젝트가 없습니다.")
        print("씬의 모든 오브젝트를 대상으로 처리하시겠습니까? (y/n)")
        print("(스크립트에서는 자동으로 모든 오브젝트 처리)")
        
        result = rename_all_actions_to_object_name()
    
    print(f"\n실행 결과: {result}")
    
    # 처리 후 액션 목록 출력
    print("\n현재 씬의 액션 목록:")
    for i, action in enumerate(bpy.data.actions, 1):
        users_count = action.users
        print(f"  {i}. '{action.name}' (사용자: {users_count}개)")