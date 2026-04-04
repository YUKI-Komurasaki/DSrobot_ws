#!/bin/bash
# 1. CAN初期化
bash ./init_can.sh

# 2. 共有メモリ初期化
sudo rm -f /dev/shm/can_motor_speed

# 3. 環境ロード
source /opt/ros/humble/setup.bash
source ~/DSrobot_ws/install/setup.bash

# 4. ネイティブ送信機起動
python3 ~/DSrobot_ws/src/my_robot_controller/scripts/native_can_sender.py &
SENDER_PID=$!

# 5. システム起動
ros2 launch my_robot_controller full_system.launch.py

# 終了時処理
kill $SENDER_PID