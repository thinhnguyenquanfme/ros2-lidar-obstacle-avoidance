import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoidance(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance')
        
        # sub to lidar scan
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
            
        # pub to control wheels
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)

    def get_sector_min_distance(self, ranges, angle_min, angle_max, angle_increment, start_angle_deg, end_angle_deg, range_min, range_max):
        # degrees to radians
        start_rad = math.radians(start_angle_deg)
        end_rad = math.radians(end_angle_deg)
        
        # map angles to array index
        start_idx = int((start_rad - angle_min) / angle_increment)
        end_idx = int((end_rad - angle_min) / angle_increment)
        
        # slice the array for this specific sector
        sector_ranges = ranges[start_idx:end_idx]
        
        # ignore inf, nan, and out-of-range values
        valid_ranges = [d for d in sector_ranges if math.isfinite(d) and range_min <= d <= range_max]
        
        if valid_ranges:
            return min(valid_ranges)
        # return infinity if nothing is in range
        return float('inf') 

    def scan_callback(self, msg):
        # 1. get min distance in the 3 sectors (front, left, right)
        front_dist = self.get_sector_min_distance(msg.ranges, msg.angle_min, msg.angle_max, msg.angle_increment, -20, 20, msg.range_min, msg.range_max)
        left_dist = self.get_sector_min_distance(msg.ranges, msg.angle_min, msg.angle_max, msg.angle_increment, 20, 90, msg.range_min, msg.range_max)
        right_dist = self.get_sector_min_distance(msg.ranges, msg.angle_min, msg.angle_max, msg.angle_increment, -90, -20, msg.range_min, msg.range_max)
        
        # 2. simple reactive brain (from readme)
        cmd = Twist()
        
        if front_dist == float('inf') or front_dist >= 0.60:
            # clear path, keep moving
            cmd.linear.x = 0.20
            cmd.angular.z = 0.0
            self.get_logger().info(f'Front clear ({front_dist:.2f}m). MOVING FORWARD.')
            
        else:
            # obstacle too close! stop and turn
            cmd.linear.x = 0.0
            if left_dist > right_dist:
                # left looks better, turn left
                cmd.angular.z = 0.60
                self.get_logger().info(f'Obstacle ahead ({front_dist:.2f}m). Left clearer. TURNING LEFT.')
            else:
                # right looks better, turn right
                cmd.angular.z = -0.60
                self.get_logger().info(f'Obstacle ahead ({front_dist:.2f}m). Right clearer. TURNING RIGHT.')

        # 3. send velocity command
        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

