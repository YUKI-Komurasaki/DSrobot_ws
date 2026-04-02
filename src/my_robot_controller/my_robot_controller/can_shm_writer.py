import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from multiprocessing import shared_memory
import numpy as np

class CanShmWriter(Node):
    def __init__(self):
        super().__init__('can_shm_writer')
        self.shm_name = 'can_motor_speed'
        
        # 共有メモリの作成/接続 (int16 x 4輪 = 8バイト)
        try:
            self.shm = shared_memory.SharedMemory(name=self.shm_name, create=True, size=8)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.shm_name)
        
        self.shared_data = np.ndarray((4,), dtype=np.int16, buffer=self.shm.buf)
        self.shared_data[:] = [0, 0, 0, 0] # 初期化
        
        self.subscription = self.create_subscription(
            Float32MultiArray, 'motor_speeds', self.callback, 10)
        self.get_logger().info('✅ CAN SHM Writer: Ready')

    def callback(self, msg):
        # m/s -> mm/s 変換
        self.shared_data[:] = [int(val * 1000) for val in msg.data]

    def __del__(self):
        if hasattr(self, 'shm'):
            self.shm.close()

def main(args=None):
    rclpy.init(args=args)
    node = CanShmWriter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shared_data[:] = [0, 0, 0, 0]
        node.destroy_node()
        rclpy.shutdown()