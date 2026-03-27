import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32MultiArray
import math

class ArmControllerNode(Node):
    def __init__(self):
        super().__init__('arm_controller_node')
        self.subscription = self.create_subscription(Joy, 'joy', self.joy_callback, 10)
        self.publisher_ = self.create_publisher(Float32MultiArray, 'arm_angles', 10)

        # リンクの長さ (mm)
        self.L1 = 118.40
        self.L2 = 128.455

        # 現在の目標座標 (初期位置: 適当に計算可能な位置)
        self.cur_x = 150.0
        self.cur_z = 50.0
        self.hand_angle = 90.0 # ハンド初期値

    def solve_ik(self, x, z):
        # 逆運動学の計算 (余弦定理を使用)
        d2 = x**2 + z**2
        d = math.sqrt(d2)

        if d > (self.L1 + self.L2) or d < abs(self.L1 - self.L2):
            self.get_logger().warn('Target out of reach!')
            return None

        # 肘の角度 (theta2)
        cos_theta2 = (d2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        theta2 = math.acos(clip(cos_theta2, -1.0, 1.0))

        # 肩の角度 (theta1)
        alpha = math.atan2(z, x)
        beta = math.acos(clip((self.L1**2 + d2 - self.L2**2) / (2 * self.L1 * d), -1.0, 1.0))
        theta1 = alpha + beta

        # ラジアンから度数法へ
        return math.degrees(theta1), math.degrees(theta2)

    def joy_callback(self, msg):
        # 十字キーの入力を取得 (Axes[4]: 左右, Axes[5]: 上下)
        dx = msg.axes[4] * 2.0  # 感度調整用
        dz = msg.axes[5] * 2.0

        self.cur_x += dx
        self.cur_z += dz

        angles = self.solve_ik(self.cur_x, self.cur_z)
        
        if angles:
            th1, th2 = angles
            # 手首(th3)は常に水平を保つ例: -(th1 + th2)
            th3 = -(th1 + th2) + 90.0 

            msg_out = Float32MultiArray()
            msg_out.data = [float(th1), float(th2), float(th3)]
            self.publisher_.publish(msg_out)

def clip(n, minn, maxn):
    return max(min(n, maxn), minn)

def main(args=None):
    rclpy.init(args=args)
    node = ArmControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    pass

if __name__ == '__main__':
    main()