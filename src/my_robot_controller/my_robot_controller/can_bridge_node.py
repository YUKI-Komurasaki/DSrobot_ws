import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import struct
import can

class CanBridgeNode(Node):
    def __init__(self):
        super().__init__('can_bridge_node')
        
        # CANバスの初期化
        # Jetson実機で使用する場合は 'can0'、PCでのシミュレーションなら 'vcan0' に設定します
        try:
            self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
            self.get_logger().info('CAN Bridge Node: Connected to can0 (Jetson Mode).')
        except Exception as e:
            self.get_logger().error(f'Failed to connect to CAN bus: {e}')
            self.get_logger().warn('Falling back to vcan0 for testing...')
            try:
                self.bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
            except:
                self.get_logger().error('CAN interface not found. Please check your hardware/vcan settings.')

        # multi_mode_teleop_node からの速度指令を購読
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'motor_speeds',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        """
        受信した [FL, FR, RL, RR] (m/s) を
        16bit signed int (mm/s) に変換してCAN送信する
        """
        # 1. データのスケーリング (m/s -> mm/s)
        # 4輪分を整数型に変換
        try:
            speeds_mm_s = [int(val * 1000) for val in msg.data]

            # 2. バイナリデータへのパッキング
            # '<hhhh' : リトルエンディアン, 2byte符号付き整数(short) x 4
            # これにより合計8バイトのデータが生成される
            can_data = struct.pack('<hhhh', *speeds_mm_s)
            
            # 3. CANメッセージの作成 (ID: 0x100)
            can_msg = can.Message(
                arbitration_id=0x100, 
                data=can_data, 
                is_extended_id=False
            )
            
            # 4. 送信
            self.bus.send(can_msg)
            
            # デバッグログ (16進数で表示)
            # hex_data = can_data.hex(' ')
            # self.get_logger().info(f'Sent CAN ID:0x100 Data: [ {hex_data} ]')
            
        except struct.error as e:
            self.get_logger().error(f'Struct Pack Error: {e}')
        except Exception as e:
            self.get_logger().error(f'CAN Send Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = CanBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('CAN Bridge Node stopping...')
    finally:
        # 終了時にモーターを止めるための安全策（全輪0速度を送信）
        try:
            stop_data = struct.pack('<hhhh', 0, 0, 0, 0)
            stop_msg = can.Message(arbitration_id=0x100, data=stop_data)
            node.bus.send(stop_msg)
        except:
            pass
            
        node.destroy_node()
        rclpy.shutdown()
    pass

if __name__ == '__main__':
    main()