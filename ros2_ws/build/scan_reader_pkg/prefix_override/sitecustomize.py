import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/thinhnguyen/ros2-lidar-obstacle-avoidance/ros2_ws/install/scan_reader_pkg'
