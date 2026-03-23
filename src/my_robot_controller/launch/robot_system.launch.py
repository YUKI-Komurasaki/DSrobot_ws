import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # パッケージ名の設定
    package_name = 'my_robot_controller'

    return LaunchDescription([
        # 1. ジョイスティックドライバ (PS4コントローラ)
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[{
                'deadzone': 0.1,    # スティックの遊び設定
                'autorepeat_rate': 20.0  # 送信頻度(Hz)
            }]
        ),

        # 2. カメラノード (V4L2)
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='v4l2_camera',
            parameters=[{
                'video_device': '/dev/video0',
                'image_size': [640, 480]
            }]
        ),

        # 3. ArUco解析ノード (自動追従用)
        Node(
            package=package_name,
            executable='aruco_node',
            name='aruco_node'
        ),

        # 4. モード切替・テレオペノード (足回りの司令塔)
        Node(
            package=package_name,
            executable='multi_teleop_node',
            name='multi_teleop_node'
        ),

        # 5. アーム制御ノード (十字キーによる逆運動学制御)
        Node(
            package=package_name,
            executable='arm_controller_node',
            name='arm_controller_node'
        ),

        # 6. CANブリッジノード (実機へのデータ送信)
        Node(
            package=package_name,
            executable='can_bridge_node',
            name='can_bridge_node'
        )
    ])