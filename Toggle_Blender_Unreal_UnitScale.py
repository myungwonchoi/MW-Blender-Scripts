import bpy

def show_message_dialog(message, title="알림", icon='INFO'):
    """메시지 다이얼로그를 띄우는 함수"""
    def draw(self, context):
        lines = message.split('\n')
        for line in lines:
            self.layout.label(text=line)
    
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def toggle_unreal_units():
    """단순 함수 버전 - 스크립트 직접 실행용"""
    scene = bpy.context.scene
    current_scale = scene.unit_settings.scale_length
    
    # 현재 상태 확인 및 출력
    print(f"현재 Unit Scale: {current_scale}")
    print(f"현재 Length Unit: {scene.unit_settings.length_unit}")
    
    # Unit Scale이 1인 경우 (블렌더 기본) → 언리얼 엔진용으로 변경
    if abs(current_scale - 1.0) < 1e-6:
        scene.unit_settings.scale_length = 0.01
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.length_unit = 'CENTIMETERS'
        # 메시지 출력 및 다이얼로그
        message = "언리얼 엔진 Unit으로 변경되었습니다\nScale: 0.01, Centimeters"
        show_message_dialog(message, "Unit 변경 완료", 'INFO')
        
    # Unit Scale이 0.01인 경우 (언리얼 엔진용) → 블렌더 기본으로 변경
    elif abs(current_scale - 0.01) < 1e-6:
        scene.unit_settings.scale_length = 1.0
        scene.unit_settings.system = 'METRIC'
        # 메시지 출력 및 다이얼로그
        scene.unit_settings.length_unit = 'CENTIMETERS'

        message = "블렌더 기본 Unit으로 변경되었습니다\nScale: 1.0"
        show_message_dialog(message, "Unit 변경 완료", 'INFO')
        
    # 그 외의 경우
    else:
        scene.unit_settings.scale_length = 1.0
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.length_unit = 'CENTIMETERS'
        # 메시지 출력 및 다이얼로그
        message = "비표준 Unit Scale 감지\n블렌더 기본 Unit으로 리셋되었습니다\nScale: 1.0"
        show_message_dialog(message, "Unit 리셋 완료", 'ERROR')
    
    # 변경 후 상태 출력
    print(f"변경된 Unit Scale: {scene.unit_settings.scale_length}")
    print(f"변경된 Length Unit: {scene.unit_settings.length_unit}")
    
    return {'FINISHED'}



# 메인 실행 부분
if __name__ == "__main__":
    toggle_unreal_units()