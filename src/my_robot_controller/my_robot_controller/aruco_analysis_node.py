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
        
        # オリジナルの映像を購読
        self.subscription = self.create_subscription(
            Image, 'image_raw', self.image_callback, 10)
        
        # モーター速度命令のパブリッシャー
        self.publisher_ = self.create_publisher(
            Float32MultiArray, 'aruco_speeds', 10)
            
        # ★追加：枠線を描き込んだ「加工済み映像」のパブリッシャー
        self.image_pub = self.create_publisher(
            Image, 'image_with_markers', 10)
        
        self.bridge = CvBridge()
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()

        # --- 制御パラメータ ---
        self.target_width_ratio = 0.25  # 目標サイズ
        self.deadzone_x = 0.05
        self.deadzone_dist = 0.02
        
        self.last_detection_time = time.time()
        self.get_logger().info('Aruco Analysis Node with Foxglove View started.')

    def image_callback(self, msg):
        # ROSの画像をOpenCV形式に変換
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        h, w, _ = frame.shape
        center_x_ref = w / 2.0 
        
        vx, vy, omega = 0.0, 0.0, 0.0
        corners, ids, _ = aruco.detectMarkers(frame, self.aruco_dict, parameters=self.parameters)
        
        if ids is not None:
            self.last_detection_time = time.time() 
            
            # 最初のマーカーで制御計算
            c = corners[0][0]
            marker_center_x = c[:, 0].mean() 
            marker_width = abs(c[0][0] - c[1][0]) 
            
            # 誤差計算
            error_x = (marker_center_x - center_x_ref) / (w / 2.0)
            error_dist = (self.target_width_ratio * w - marker_width) / (self.target_width_ratio * w)

            # P制御
            if abs(error_x) > self.deadzone_x:
                omega = -error_x * 0.7
            if abs(error_dist) > self.deadzone_dist:
                vx = error_dist * 0.5

            # ★フレームに枠線と情報を描き込む
            aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.putText(frame, f"Vx:{vx:.2f} W:{omega:.2f}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        else:
            # 見失ったら停止（0.5秒猶予）
            if time.time() - self.last_detection_time > 0.5:
                vx, vy, omega = 0.0, 0.0, 0.0

        # --- メカナム逆運動学 ---
        v_fl = vx - vy - omega
        v_fr = vx + vy + omega
        v_rl = vx + vy - omega
        v_rr = vx - vy + omega
        
        # モーター速度を送信
        speed_msg = Float32MultiArray()
        speed_msg.data = [float(v_fl), float(v_fr), float(v_rl), float(v_rr)]
        self.publisher_.publish(speed_msg)
        
        # ★追加：加工後の画像をROSメッセージに変換してFoxgloveへ送る
        annotated_image_msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
        # 元のタイムスタンプを引き継ぐ（重要）
        annotated_image_msg.header = msg.header
        self.image_pub.publish(annotated_image_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoToMotorSpeedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 終了時に停止
        stop_msg = Float32MultiArray()
        stop_msg.data = [0.0, 0.0, 0.0, 0.0]
        node.publisher_.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()
        pass

if __name__ == '__main__':
    main()