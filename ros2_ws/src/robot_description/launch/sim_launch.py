import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    pkg_robot_description = get_package_share_directory('robot_description')
    
    # get path to sdf file
    world_file = os.path.join(pkg_robot_description, 'worlds', 'car_worlds.sdf')
    
    # 1. run gazebo. using cpu rendering hack because wsl2 gpu is laggy here
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', world_file],
        additional_env={
            'QT_QPA_PLATFORM': 'xcb',
            'LIBGL_ALWAYS_SOFTWARE': '1'
        },
        output='screen'
    )
    
    # 2. ros-gz bridge. need this to pass /scan and /cmd_vel between ros2 and gazebo
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist'
        ],
        output='screen'
    )
    
    # 3. run my simple obstacle avoidance node
    obstacle_avoidance = Node(
        package='scan_reader_pkg',
        executable='obstacle_avoidance',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        bridge,
        obstacle_avoidance
    ])

