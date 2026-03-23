import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # launchファイルをインストール対象に含める設定
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yuki-komurasaki',
    maintainer_email='yuki-komurasaki@todo.todo',
    description='My Robot Control Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # ノード名 = パッケージ名.ファイル名:関数名
            'can_bridge_node = my_robot_controller.can_bridge_node:main',
            'multi_teleop_node = my_robot_controller.multi_mode_teleop_node:main',
            'aruco_node = my_robot_controller.aruco_analysis_node:main',
            'arm_controller_node = my_robot_controller.arm_controller_node:main',
        ],
    },
)