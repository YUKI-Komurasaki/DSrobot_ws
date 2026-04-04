import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage # 圧縮版に変更
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import cv2.aruco as aruco
import numpy as np

class ArucoAnalysisNode(Node):
    def __init__(self):
        super().__init__('aruco_node')
        # 圧縮トピックを購読するように変更
        self.subscription = self.create_subscription(
            CompressedImage, '/image_raw/compressed', self.image_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/aruco_speeds', 10)
        self.bridge = CvBridge()
        
        # OpenCVのバージョン互換性対応
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        try:
            self.parameters = aruco.DetectorParameters_create() # 古いVer
        except AttributeError:
            self.parameters = aruco.DetectorParameters() # 新しいVer

        self.target_ids = [0, 1, 2, 3]
        self.current_index = 0
        self.stop_distance = 0.20
        self.marker_size = 0.1
        self.cam_matrix = np.array([[600, 0, 320], [0, 600, 240], [0, 0, 1]], dtype=float)
        self.dist_coeffs = np.zeros((5, 1))

    def image_callback(self, msg):
        self.get_logger().info('画像を受信しました！')
        # 圧縮データをデコード
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 検出
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        
        twist = Twist()
        found = False
        if ids is not None:
            for i, m_id in enumerate(ids.flatten()):
                if m_id == self.target_ids[self.current_index]:
                    found = True
                    rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], self.marker_size, self.cam_matrix, self.dist_coeffs)
                    dist = tvec[0][0][2]
                    if dist > self.stop_distance:
                        twist.linear.x = 0.15
                        twist.angular.z = -tvec[0][0][0] * 3.0
                    else:
                        self.current_index = (self.current_index + 1) % len(self.target_ids)
                    break
        
        if not found:
            twist.angular.z = 0.4 # 探して旋回
            
        self.publisher_.publish(twist)
        
# (クラス定義 ArucoAnalysisNode の後、一番左のインデントで書く)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoAnalysisNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()