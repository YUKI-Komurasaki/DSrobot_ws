import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32MultiArray

class MultiModeTeleopNode(Node):
    def __init__(self):
        super().__init__('multi_mode_teleop_node')
        
        # ジョイスティックとArUcoの両方を購読
        self.joy_sub = self.create_subscription(Joy, 'joy', self.joy_callback, 10)
        self.aruco_sub = self.create_subscription(Float32MultiArray, 'aruco_speeds', self.aruco_callback, 10)
        
        # 最終的なモーター指令だけをパブリッシュ
        self.publisher_ = self.create_publisher(Float32MultiArray, 'motor_speeds', 10)
        
        self.auto_mode = False
        self.last_button_state = 0
        self.aruco_val = [0.0, 0.0, 0.0, 0.0] # ArUcoからの最新値を保持

        self.get_logger().info('Mode: MANUAL (Press X to toggle AUTO)')

    def aruco_callback(self, msg):
        # ArUcoノードからの計算結果（4輪分）をメモしておく
        self.aruco_val = msg.data

    def joy_callback(self, msg):
        # ×ボタン(index 0)でモード切替
        if msg.buttons[0] == 1 and self.last_button_state == 0:
            self.auto_mode = not self.auto_mode
            status = "AUTO (ArUco)" if self.auto_mode else "MANUAL (Joystick)"
            self.get_logger().info(f'Switched to {status}')
        self.last_button_state = msg.buttons[0]

        speed_msg = Float32MultiArray()

        if self.auto_mode:
            # 自動モードなら、保存しておいたArUcoの値を採用
            speed_msg.data = list(self.aruco_val)
        else:
            # 手動モードなら、スティックから計算
            vx = msg.axes[1]    # L上下
            vy = msg.axes[0]    # L左右
            omega = msg.axes[2] # R左右
            
            v_fl = vx - vy - omega
            v_fr = vx + vy + omega
            v_rl = vx + vy - omega
            v_rr = vx - vy + omega
            speed_msg.data = [float(v_fl), float(v_fr), float(v_rl), float(v_rr)]

        self.publisher_.publish(speed_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MultiModeTeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()