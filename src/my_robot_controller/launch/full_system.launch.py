from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # SHM Writer
        Node(package='my_robot_controller', executable='can_shm_writer', name='can_shm_writer'),
        # Teleop
        Node(package='my_robot_controller', executable='multi_mode_teleop_node', name='teleop_node'),
        # Joy Driver
        Node(package='joy', executable='joy_node', name='joy_node', parameters=[{'deadzone': 0.05}]),
        # Camera
        Node(package='v4l2_camera', executable='v4l2_camera_node', name='camera_node', 
             parameters=[{'video_device': '/dev/video0'}]),
        # Foxglove
        Node(package='foxglove_bridge', executable='foxglove_bridge', name='foxglove_bridge'),
    ])