from setuptools import setup
import os
from glob import glob

package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Launchファイルのインストール
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robopro',
    maintainer_email='robopro@todo.todo',
    description='Jetson Orin Nano Robot Controller with SHM CAN',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'can_shm_writer = my_robot_controller.can_shm_writer:main',
            'multi_mode_teleop_node = my_robot_controller.multi_mode_teleop_node:main',
        ],
    },
)