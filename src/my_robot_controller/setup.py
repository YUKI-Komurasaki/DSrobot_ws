from setuptools import setup
import os
from glob import glob

package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Launchファイルをインストール対象に含める
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robopro',
    maintainer_email='robopro@todo.todo',
    description='Robot Control Package with CAN and Arm Support',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'analysis = my_robot_controller.analysis:main',
            'teleop = my_robot_controller.teleop:main',
            'can_bridge_node = my_robot_controller.can_bridge_node:main',
            'arm_controller_node.py = my_robot_controller.arm_controller_node:main',
        ],
    },
)