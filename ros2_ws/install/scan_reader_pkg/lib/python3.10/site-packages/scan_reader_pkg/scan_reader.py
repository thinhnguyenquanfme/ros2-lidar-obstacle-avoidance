import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ScanReader(Node):
    def __init__(self):
        super().__init__('scan_reader')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.subscription  # prevent unused variable warning

    def scan_callback(self, msg):
        valid_ranges = [distance for distance in msg.ranges if math.isfinite(distance) 
                        and msg.range_min <= distance <= msg.range_max]
        if valid_ranges:
            self.get_logger().info(f'Minimum distance: {min(valid_ranges):.2f} m')

def main(args=None):
    rclpy.init(args=args)
    scan_reader = ScanReader()
    rclpy.spin(scan_reader)
    scan_reader.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()