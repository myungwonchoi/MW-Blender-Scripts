import bpy

def rename_action_slots_to_object_name():
    """
    선택된 오브젝트들의 액션 슬롯 name_display를 해당 오브젝트 이름으로 변경하는 함수
    (블렌더 4.4+ 액션 슬롯 시스템 대응)
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
        
        # 현재 오브젝트에 적용된 슬롯만 처리 (블렌더 4.4+)
        print(f"  - 액션 '{action.name}'에서 현재 오브젝트의 슬롯을 처리합니다.")
        
        if not hasattr(action, 'slots') or not action.slots:
            print(f"  - 액션에 슬롯이 없습니다.")
            continue
        
        # 현재 오브젝트에 할당된 슬롯 찾기
        current_slot = None
        if hasattr(obj.animation_data, 'action_slot_handle'):
            slot_handle = obj.animation_data.action_slot_handle
            # 슬롯 핸들을 통해 현재 슬롯 찾기
            for slot in action.slots:
                if slot.handle == slot_handle:
                    current_slot = slot
                    break
        
        if current_slot:
            old_slot_name = current_slot.name_display
            current_slot.name_display = obj.name
            print(f"    - 현재 슬롯 name_display 변경: '{old_slot_name}' → '{current_slot.name_display}'")
            processed_count += 1
        else:
            print(f"  - 현재 오브젝트에 할당된 슬롯을 찾을 수 없습니다.")
            continue
        
        # NLA 트랙의 현재 오브젝트에 할당된 슬롯들도 확인하고 변경
        if obj.animation_data.nla_tracks:
            for track in obj.animation_data.nla_tracks:
                for strip in track.strips:
                    if strip.action and hasattr(strip.action, 'slots') and strip.action.slots:
                        # NLA 스트립에서 현재 오브젝트에 할당된 슬롯 찾기
                        if hasattr(strip, 'action_slot_handle'):
                            strip_slot_handle = strip.action_slot_handle
                            for slot in strip.action.slots:
                                if slot.handle == strip_slot_handle:
                                    old_slot_name = slot.name_display
                                    slot.name_display = obj.name
                                    print(f"    - NLA 슬롯 name_display 변경: '{old_slot_name}' → '{slot.name_display}'")
                                    break
    
    if processed_count > 0:
        print(f"\n총 {processed_count}개의 오브젝트에서 액션 슬롯 name_display가 변경되었습니다.")
    else:
        print("\n변경된 슬롯이 없습니다. 선택된 오브젝트들에 액션이 없거나 애니메이션 데이터가 없습니다.")
    
    return {'FINISHED'}

# 메인 실행 부분
if __name__ == "__main__":
    rename_action_slots_to_object_name()