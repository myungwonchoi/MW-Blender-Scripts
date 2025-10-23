import bpy

# 1. 활성화된(Active) 오브젝트를 가져옵니다. (Child Of Constraint를 받을 대상)
active_obj = bpy.context.view_layer.objects.active

if active_obj is None:
    print("WARNING: 활성화된 오브젝트가 없습니다. 스크립트를 실행할 수 없습니다.")
else:
    # 2. 새로운 Empty 오브젝트를 'Cube' 모양으로 생성합니다.
    bpy.ops.object.empty_add(type='CUBE', location=(0, 0, 0))
    
    # 3. 새로 생성된 Empty 오브젝트를 참조합니다. (Child Of Constraint의 타겟)
    new_empty = bpy.context.view_layer.objects.active
    new_empty.name = "CTRL_" + active_obj.name
    
    # 3-1. Empty의 viewport display 설정: In Front 활성화
    new_empty.show_in_front = True
    
    # 4. 트랜스폼(위치, 회전, 스케일)을 복사하고 부모 관계를 상속합니다.
    # Empty가 원본 오브젝트와 완벽하게 겹치게 됩니다.
    new_empty.matrix_world = active_obj.matrix_world
    new_empty.parent = active_obj.parent
    
    # 부모가 있는 경우, Parent Inverse를 설정하여 트랜스폼 일관성을 유지합니다.
    if active_obj.parent:
        new_empty.matrix_parent_inverse = active_obj.parent.matrix_world.inverted()
        
    # --- 콜렉션 처리 (이전 로직 유지) ---
    
    target_collections = active_obj.users_collection
    current_collections = list(new_empty.users_collection)

    for col in target_collections:
        if new_empty.name not in col.objects: 
            col.objects.link(new_empty)

    for col in current_collections:
        if col not in target_collections:
            if new_empty.name in col.objects:
                col.objects.unlink(new_empty)
    
    # --- 추가된 부분: Child Of Constraint 설정 ---
    
    # 9. 원본 오브젝트(active_obj)를 선택하고 활성화합니다. (제약 조건 추가를 위해)
    new_empty.select_set(False)
    active_obj.select_set(True)
    bpy.context.view_layer.objects.active = active_obj
    
    # 10. active_obj에 'Child Of' 제약 조건을 추가합니다.
    constraint = active_obj.constraints.new(type='CHILD_OF')
    
    # 11. 타겟을 새로 생성된 Empty로 지정합니다.
    constraint.target = new_empty
    
    # 12. 현재 월드 트랜스폼을 유지하도록 'Set Inverse'를 실행합니다.
    # 이 과정이 없다면, 오브젝트가 Empty의 로컬 트랜스폼을 따라가기 위해 갑자기 엉뚱한 위치로 이동합니다.
    bpy.ops.constraint.childof_set_inverse(constraint=constraint.name, owner='OBJECT')

    # 13. 최종적으로 Empty 오브젝트를 선택하고 활성화합니다.
    active_obj.select_set(False)
    new_empty.select_set(True)
    bpy.context.view_layer.objects.active = new_empty
    
    print(f"INFO: '{new_empty.name}' Empty가 생성되었고, 원본 오브젝트에 Child Of 제약 조건이 설정되었습니다. Empty가 선택 및 활성화되었습니다.")