import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. カメラ (MJPEG圧縮)
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='v4l2_camera',
            parameters=[{
                'video_device': '/dev/video0',
                'image_size': [640, 480],
                'pixel_format': 'mjpeg',
                'output_encoding': 'rgb8',
            }]
        ),

        # 2. ArUco解析
        Node(
            package='my_robot_controller',
            executable='analysis',
            name='aruco_analysis_node',
        ),

        # 3. テレオペ
        Node(
            package='my_robot_controller',
            executable='teleop',
            name='multi_mode_teleop_node',
        ),

        # 4. CAN通信
        Node(
            package='my_robot_controller',
            executable='can_bridge_node',
            name='can_communication_node',
            parameters=[{'interface': 'can0'}]
        ),

        # 5. アーム操作
        Node(
            package='my_robot_controller',
            executable='arm_controller_node.py',
            name='arm_operation_node',
        ),

        # 6. ジョイスティック
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
        ),

        # 7. Foxglove Bridge (ラグ対策版)
        Node(
            package='foxglove_bridge',
            executable='foxglove_bridge',
            name='foxglove_bridge',
            parameters=[{
                'port': 8765,
                'address': '0.0.0.0',
                'use_compression': True,
                'send_buffer_limit': 1000000,
            }]
        ),
    ])