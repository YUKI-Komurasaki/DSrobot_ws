from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 既存のノード
        Node(package='my_robot_controller', executable='can_shm_writer', name='can_shm_writer'),
        Node(package='my_robot_controller', executable='multi_mode_teleop_node', name='teleop_node'),
        Node(package='my_robot_controller', executable='aruco_analysis_node', name='aruco_node'),
        
        Node(package='joy', executable='joy_node', name='joy_node', parameters=[{'deadzone': 0.05}]),
        Node(package='foxglove_bridge', executable='foxglove_bridge', name='foxglove_bridge'),
        
        # カメラノード（もしエラーが出るならパラメータを確認してください）
        Node(package='v4l2_camera', executable='v4l2_camera_node', name='camera_node', 
             parameters=[{'video_device': '/dev/video1'}])
    ])