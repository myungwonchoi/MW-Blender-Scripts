import bpy

# 1. 활성화된(Active) 오브젝트를 가져옵니다.
active_obj = bpy.context.view_layer.objects.active

if active_obj is None:
    print("WARNING: 활성화된 오브젝트가 없습니다. 스크립트를 실행할 수 없습니다.")
else:
    # 2. 새로운 Empty 오브젝트를 'Cube' 모양으로 생성합니다.
    # 오브젝트 생성 (처음에는 활성화된 뷰 레이어의 콜렉션에 생성됨)
    bpy.ops.object.empty_add(type='CUBE', location=(0, 0, 0))
    
    # 3. 새로 생성된 Empty 오브젝트를 참조합니다.
    new_empty = bpy.context.view_layer.objects.active
    new_empty.name = active_obj.name + "_Empty" # 이름 설정
    
    # 4. 트랜스폼(위치, 회전, 스케일)을 복사하고 부모 관계를 상속합니다.
    new_empty.matrix_world = active_obj.matrix_world
    new_empty.parent = active_obj.parent
    
    # 부모가 있는 경우, 로컬 트랜스폼 일관성을 위해 Parent Inverse를 설정합니다.
    if active_obj.parent:
        new_empty.matrix_parent_inverse = active_obj.parent.matrix_world.inverted()
        
    # --- 콜렉션 처리 ---
    
    # 5. 선택된 오브젝트가 현재 속해있는 모든 콜렉션을 가져옵니다.
    target_collections = active_obj.users_collection
    
    # 6. 새로 생성된 Empty가 현재 속한 콜렉션을 먼저 저장합니다.
    current_collections = list(new_empty.users_collection)

    # 7. Empty를 원본 오브젝트의 모든 콜렉션에 추가합니다.
    for col in target_collections:
        if new_empty.name not in col.objects: 
            col.objects.link(new_empty)

    # 8. Empty를 원래 생성되었던 불필요한 콜렉션에서 제거합니다.
    for col in current_collections:
        if col not in target_collections:
            if new_empty.name in col.objects:
                col.objects.unlink(new_empty)
    
    # --- 수정된 부분: 새로 생성된 Empty를 선택하도록 처리 ---
    
    # 9. 기존에 선택되었던 오브젝트의 선택을 해제합니다.
    active_obj.select_set(False)
    
    # 10. 새로 생성된 Empty를 선택하고 활성화합니다. (이미 3번에서 활성화되어 있으나, 확실히 처리)
    new_empty.select_set(True)
    bpy.context.view_layer.objects.active = new_empty
    
    print(f"INFO: '{new_empty.name}' 오브젝트가 생성되었고, 현재 선택 및 활성화되었습니다.")