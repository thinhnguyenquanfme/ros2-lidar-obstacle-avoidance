import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoidance(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance')
        
        # Nhận dữ liệu Lidar
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
            
        # Gửi lệnh điều khiển bánh xe
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)

    def get_sector_min_distance(self, ranges, angle_min, angle_max, angle_increment, start_angle_deg, end_angle_deg, range_min, range_max):
        # Đổi độ sang radian
        start_rad = math.radians(start_angle_deg)
        end_rad = math.radians(end_angle_deg)
        
        # Tìm chỉ số mảng (index) tương ứng với góc
        start_idx = int((start_rad - angle_min) / angle_increment)
        end_idx = int((end_rad - angle_min) / angle_increment)
        
        # Cắt lấy mảng khoảng cách của vùng đó
        sector_ranges = ranges[start_idx:end_idx]
        
        # Lọc các giá trị hợp lệ
        valid_ranges = [d for d in sector_ranges if math.isfinite(d) and range_min <= d <= range_max]
        
        if valid_ranges:
            return min(valid_ranges)
        return float('inf') # Nếu không có vật cản nào hợp lệ thì coi như vô cực

    def scan_callback(self, msg):
        # 1. Tính toán khoảng cách gần nhất ở 3 vùng theo đúng README
        front_dist = self.get_sector_min_distance(msg.ranges, msg.angle_min, msg.angle_max, msg.angle_increment, -20, 20, msg.range_min, msg.range_max)
        left_dist = self.get_sector_min_distance(msg.ranges, msg.angle_min, msg.angle_max, msg.angle_increment, 20, 90, msg.range_min, msg.range_max)
        right_dist = self.get_sector_min_distance(msg.ranges, msg.angle_min, msg.angle_max, msg.angle_increment, -90, -20, msg.range_min, msg.range_max)
        
        # 2. Quyết định vận tốc (Logic từ README phần 4)
        cmd = Twist()
        
        if front_dist == float('inf') or front_dist >= 0.60:
            # Đường trống hoặc không thấy vật cản nào trong tầm nhìn -> Đi thẳng
            cmd.linear.x = 0.20
            cmd.angular.z = 0.0
            self.get_logger().info(f'Front clear ({front_dist:.2f}m). MOVING FORWARD.')
            
        else:
            # Có vật cản phía trước mặt (dưới 0.6m) -> Phanh lại và Rẽ
            cmd.linear.x = 0.0
            if left_dist > right_dist:
                # Bên trái thoáng hơn -> Rẽ trái (+0.6 rad/s)
                cmd.angular.z = 0.60
                self.get_logger().info(f'Obstacle ahead ({front_dist:.2f}m). Left clearer. TURNING LEFT.')
            else:
                # Bên phải thoáng hơn -> Rẽ phải (-0.6 rad/s)
                cmd.angular.z = -0.60
                self.get_logger().info(f'Obstacle ahead ({front_dist:.2f}m). Right clearer. TURNING RIGHT.')

        # 3. Gửi lệnh đi
        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

