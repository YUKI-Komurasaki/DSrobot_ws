import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/yuki-komurasaki/DSrobot_ws/install/my_robot_controller'
