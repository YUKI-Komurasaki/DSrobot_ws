import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import struct
import can

class CanBridgeNode(Node):
    def __init__(self):
        super().__init__('can_bridge_node')
        
        # CANバスの初期化 (can0を指定) 
        try:
            self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
            self.get_logger().info('CAN Bridge Node connected to can0.')
        except Exception as e:
            self.get_logger().error(f'Could not connect to CAN bus: {e}')

        self.subscription = self.create_subscription(
            Float32MultiArray,
            'motor_speeds',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        # 1. データのスケーリング (m/s -> mm/s)
        speeds_mm_s = [int(val * 1000) for val in msg.data]

        # 2. バイナリデータへの変換
        try:
            can_data = struct.pack('<hhhh', *speeds_mm_s)
            
            # 3. 実際にCANフレームを送信 (ID: 0x100)
            can_msg = can.Message(
                arbitration_id=0x100, 
                data=can_data, 
                is_extended_id=False
            )
            self.bus.send(can_msg)
            
            # 確認用のログ出力
            self.get_logger().info(f'Sent CAN ID:0x100 Data: {can_data.hex(" ")}')
            
        except Exception as e:
            self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = CanBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()