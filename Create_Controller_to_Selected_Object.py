import bpy

# 오브젝트 타입별 기본 컨트롤러 크기 설정
CONTROLLER_SIZE_MAP = {
    'LIGHT': 2.0,      # 라이트는 큰 컨트롤러
    'CAMERA': 1.5,     # 카메라는 중간 크기
    'ARMATURE': 1.0,   # 아마추어는 기본 크기
    'EMPTY': 1.0,      # Empty (콜렉션 인스턴스 포함)도 지원
    'CURVE': 0.8,      # 커브는 약간 작게
    'SURFACE': 0.8,    # 서피스도 약간 작게
    'META': 0.6,       # 메타볼은 작게
    'TEXT': 0.6,       # 텍스트도 작게
    'LATTICE': 0.5,    # 래티스는 더 작게
    'DEFAULT': 0.5     # 기타 타입의 기본값
}

def get_controller_size(obj_type, dimensions):
    """오브젝트 타입과 크기에 따른 컨트롤러 크기 계산"""
    max_dimension = max(dimensions.x, dimensions.y, dimensions.z)
    
    if max_dimension > 0:
        # dimensions가 있는 경우 실제 크기 사용
        return max_dimension * 0.5
    else:
        # dimensions가 0인 경우 타입별 기본 크기 사용
        default_size = CONTROLLER_SIZE_MAP.get(obj_type, CONTROLLER_SIZE_MAP['DEFAULT'])
        return default_size * 0.5

def create_controller_for_object(target_obj):
    """단일 오브젝트에 대해 컨트롤러를 생성하는 함수"""
    
    # 현재 선택 상태 저장
    original_selection = list(bpy.context.selected_objects)
    original_active = bpy.context.view_layer.objects.active
    
    # 모든 오브젝트 선택 해제
    bpy.ops.object.select_all(action='DESELECT')
    
    # 2. 새로운 Empty 오브젝트를 'Cube' 모양으로 생성합니다.
    bpy.ops.object.empty_add(type='CUBE', location=(0, 0, 0))
    
    # 3. 새로 생성된 Empty 오브젝트를 참조합니다. (Child Of Constraint의 타겟)
    new_empty = bpy.context.view_layer.objects.active
    new_empty.name = target_obj.name + "_CTRL"
    
    # 3-1. Empty의 viewport display 설정: In Front 활성화
    new_empty.show_in_front = True
    
    # 3-2. 바운딩 박스 크기 계산 및 Empty 크기 설정
    dimensions = target_obj.dimensions
    radius_size = get_controller_size(target_obj.type, dimensions)
    
    # 최소값 보장 (0.05)
    new_empty.empty_display_size = max(radius_size, 0.05)
    
    print(f"DEBUG: '{target_obj.name}' ({target_obj.type}) 크기 - X:{dimensions.x:.3f}, Y:{dimensions.y:.3f}, Z:{dimensions.z:.3f}")
    print(f"DEBUG: Empty '{new_empty.name}' 크기를 {radius_size:.3f}로 설정")
    
    # 4. 트랜스폼(위치, 회전, 스케일)을 복사하고 부모 관계를 상속합니다.
    # Empty가 원본 오브젝트와 완벽하게 겹치게 됩니다.
    new_empty.matrix_world = target_obj.matrix_world
    new_empty.parent = target_obj.parent
    
    # 부모가 있는 경우, Parent Inverse를 설정하여 트랜스폼 일관성을 유지합니다.ㅌ
    if target_obj.parent:
        new_empty.matrix_parent_inverse = target_obj.parent.matrix_world.inverted()
        
    # --- 콜렉션 처리 (이전 로직 유지) ---
    target_collections = target_obj.users_collection
    current_collections = list(new_empty.users_collection)

    for col in target_collections:
        if new_empty.name not in col.objects: 
            col.objects.link(new_empty)

    for col in current_collections:
        if col not in target_collections:
            if new_empty.name in col.objects:
                col.objects.unlink(new_empty)
    
    # --- 추가된 부분: Child Of Constraint 설정 ---
    
    # 9. 원본 오브젝트를 선택하고 활성화합니다. (제약 조건 추가를 위해)
    new_empty.select_set(False)
    target_obj.select_set(True)
    bpy.context.view_layer.objects.active = target_obj
    
    # 10. target_obj에 'Child Of' 제약 조건을 추가합니다.
    constraint = target_obj.constraints.new(type='CHILD_OF')
    
    # 11. 타겟을 새로 생성된 Empty로 지정합니다.
    constraint.target = new_empty
    
    # 12. 현재 월드 트랜스폼을 유지하도록 'Set Inverse'를 실행합니다.
    # 이 과정이 없다면, 오브젝트가 Empty의 로컬 트랜스폼을 따라가기 위해 갑자기 엉뚱한 위치로 이동합니다.
    bpy.ops.constraint.childof_set_inverse(constraint=constraint.name, owner='OBJECT')
    
    print(f"INFO: '{new_empty.name}' Empty가 생성되었고, '{target_obj.name}' 오브젝트에 Child Of 제약 조건이 설정되었습니다.")
    
    return new_empty


# 메인 실행 부분
selected_objects = list(bpy.context.selected_objects)

if not selected_objects:
    print("WARNING: 선택된 오브젝트가 없습니다. 스크립트를 실행할 수 없습니다.")
else:
    print(f"INFO: {len(selected_objects)}개의 선택된 오브젝트에 대해 컨트롤러를 생성합니다.")
    
    created_empties = []
    
    # 각 선택된 오브젝트에 대해 컨트롤러 생성
    for obj in selected_objects:
        # 이미 컨트롤러인 오브젝트만 제외 (이름이 "_CTRL"로 끝나는 경우)
        if obj.name.endswith("_CTRL"):
            print(f"SKIP: '{obj.name}'은(는) 이미 컨트롤러이므로 건너뜁니다.")
        else:
            empty = create_controller_for_object(obj)
            created_empties.append(empty)
            print(f"INFO: '{obj.name}' ({obj.type})에 대한 컨트롤러를 생성했습니다.")
    
    # 생성된 모든 Empty 오브젝트들을 선택
    bpy.ops.object.select_all(action='DESELECT')
    for empty in created_empties:
        empty.select_set(True)
    
    # 마지막으로 생성된 Empty를 활성화
    if created_empties:
        bpy.context.view_layer.objects.active = created_empties[-1]
        print(f"SUCCESS: 총 {len(created_empties)}개의 컨트롤러가 생성되었습니다.")
        print(f"INFO: 생성된 컨트롤러들이 모두 선택되었습니다.")