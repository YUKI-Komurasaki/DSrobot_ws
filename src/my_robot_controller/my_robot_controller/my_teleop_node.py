import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32MultiArray

class MecanumTeleopNode(Node):
    def __init__(self):
        super().__init__('mecanum_teleop_node')
        
        # 購読: joy_node からの入力
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
        
        # 公開: 各ホイールの目標速度 (FL, FR, RL, RR)
        self.publisher_ = self.create_publisher(
            Float32MultiArray, 
            'motor_speeds', 
            10)
        
        self.get_logger().info('Mecanum Teleop Node has been started.')
        self.get_logger().info('Control: Left Stick (Move), Right Stick (Turn)')

    def joy_callback(self, msg):
        # --- PS4 Controller Mapping (Standard joy_node) ---
        # msg.axes[1]: Left Stick Vertical   (Up: 1.0, Down: -1.0) -> Vx
        # msg.axes[0]: Left Stick Horizontal (Left: 1.0, Right: -1.0) -> Vy
        # msg.axes[2]: Right Stick Horizontal (Left: 1.0, Right: -1.0) -> Omega (Turn)
        
        vx = msg.axes[1]      # 前後
        vy = msg.axes[0]      # 左右スライド
        omega = msg.axes[2]   # 旋回（左に倒すと正の値＝反時計回り）

        # --- メカナムホイールの逆運動学計算 ---
        # 簡易式: 車体形状やホイール半径を1とした場合
        # フロント左 (FL) = Vx - Vy - Omega
        # フロント右 (FR) = Vx + Vy + Omega
        # リア左    (RL) = Vx + Vy - Omega
        # リア右    (RR) = Vx - Vy + Omega
        
        v_fl = vx - vy - omega
        v_fr = vx + vy + omega
        v_rl = vx + vy - omega
        v_rr = vx - vy + omega
        
        # --- メッセージの作成とパブリッシュ ---
        speed_msg = Float32MultiArray()
        speed_msg.data = [float(v_fl), float(v_fr), float(v_rl), float(v_rr)]
        self.publisher_.publish(speed_msg)
        
        # --- ログ確認 (デバッグ用) ---
        self.get_logger().info(
            f'Input: Vx:{vx:.2f} Vy:{vy:.2f} W:{omega:.2f} | '
            f'Motors: FL:{v_fl:5.2f} FR:{v_fr:5.2f} RL:{v_rl:5.2f} RR:{v_rr:5.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = MecanumTeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()