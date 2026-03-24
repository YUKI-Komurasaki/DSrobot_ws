import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge
import cv2
import cv2.aruco as aruco
import time

class ArucoToMotorSpeedNode(Node):
    def __init__(self):
        super().__init__('aruco_to_motor_speed_node')
        
        self.subscription = self.create_subscription(
            Image, 'image_raw', self.image_callback, 10)
        
        self.publisher_ = self.create_publisher(
            Float32MultiArray, 'aruco_speeds', 10)
        
        self.bridge = CvBridge()
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.parameters = aruco.DetectorParameters_create()

        # --- 制御パラメータ ---
        self.target_width_ratio = 0.25
        self.deadzone_x = 0.05
        self.deadzone_dist = 0.02
        
        self.last_detection_time = time.time()
        
        # GUI設定用パラメータの宣言
        self.declare_parameter('target_id', 0)
        
        self.get_logger().info('Aruco Node with Dynamic ID Tracking started.')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        h, w, _ = frame.shape
        center_x_ref = w / 2.0 
        
        # 現在設定されているターゲットIDをGUIから取得
        target_id = self.get_parameter('target_id').get_parameter_value().integer_value
        
        vx, vy, omega = 0.0, 0.0, 0.0
        corners, ids, _ = aruco.detectMarkers(frame, self.aruco_dict, parameters=self.parameters)
        
        found_target = False
        
        if ids is not None:
            # 見つかった全てのマーカーの中から target_id を探す
            for i, marker_id in enumerate(ids):
                if marker_id[0] == target_id:
                    found_target = True
                    self.last_detection_time = time.time()
                    
                    c = corners[i][0] # 一致したインデックスiの角を使用
                    marker_center_x = c[:, 0].mean() 
                    marker_width = abs(c[0][0] - c[1][0]) 
                    
                    # 1. 左右のズレ
                    error_x = (marker_center_x - center_x_ref) / (w / 2.0)
                    # 2. 距離のズレ
                    error_dist = (self.target_width_ratio * w - marker_width) / (self.target_width_ratio * w)

                    # P制御
                    if abs(error_x) > self.deadzone_x:
                        omega = -error_x * 0.7
                    if abs(error_dist) > self.deadzone_dist:
                        vx = error_dist * 0.5

                    # ターゲットに印を付ける
                    aruco.drawDetectedMarkers(frame, [corners[i]], ids[i])
                    cv2.putText(frame, f"TARGET ID:{target_id}", (20, 60), 1, 1, (0, 0, 255), 2)
                    break # ターゲットを見つけたらループを抜ける

        # マーカーが見つからない、またはターゲットIDではない場合
        if not found_target:
            if time.time() - self.last_detection_time > 0.5:
                vx, vy, omega = 0.0, 0.0, 0.0
            cv2.putText(frame, f"SEARCHING ID:{target_id}", (20, 60), 1, 1, (255, 0, 0), 2)

        # メカナム逆運動学
        v_fl = vx - vy - omega
        v_fr = vx + vy + omega
        v_rl = vx + vy - omega
        v_rr = vx - vy + omega
        
        speed_msg = Float32MultiArray()
        speed_msg.data = [float(v_fl), float(v_fr), float(v_rl), float(v_rr)]
        self.publisher_.publish(speed_msg)
        
        cv2.putText(frame, f"Vx:{vx:.2f} W:{omega:.2f}", (20, 30), 1, 1, (0, 255, 0), 2)
        cv2.imshow("Aruco Tracking", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoToMotorSpeedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 終了時に停止信号を送る
        stop_msg = Float32MultiArray()
        stop_msg.data = [0.0, 0.0, 0.0, 0.0]
        node.publisher_.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()