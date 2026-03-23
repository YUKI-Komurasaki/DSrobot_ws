from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. ジョイスティックドライバ (PS4コントローラ)
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[{'deadzone': 0.1}] # スティックの微小なブレを無視
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
            package='my_robot_controller',
            executable='aruco_node', # 実行ファイル名は setup.py の定義に合わせてください
            name='aruco_node'
        ),

        # 4. モード切替・テレオペノード (司令塔)
        Node(
            package='my_robot_controller',
            executable='multi_teleop_node', # setup.py の定義に合わせてください
            name='multi_teleop_node'
        ),

        # 5. CANブリッジノード (実機送信)
        Node(
            package='my_robot_controller',
            executable='can_bridge_node',
            name='can_bridge_node'
        )
    ])