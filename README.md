# ros2-lidar-obstacle-avoidance

## 1. Research Question

How can a mobile robot use 2D LiDAR measurements to detect obstacles and generate the simpliest velocity command?

## 2. Objective

Build a small ROS 2 obstacle-avoidance system that subscribes to 2D LiDAR data on `/scan`, identifies obstacles ahead, and publishes safe commands on `/cmd_vel`. The initial controller is reactive: drive forward when clear; stop and turn when an obstacle is too close.

## 3. System Architecture

```text
LiDAR source (Gazebosim)
                 |  /scan [sensor_msgs/LaserScan]
                 v
       obstacle_avoidance_node
          | filter scan and decide motion
          v
       /cmd_vel [geometry_msgs/Twist]
                 |
                 v
       robot base / simulator
```

| Node | Responsibility | Input | Output |
| --- | --- | --- | --- |
| `scan_reader` | Inspect raw scan data | `/scan` | logs |
| `obstacle_avoidance` | Decide robot motion | `/scan` | `/cmd_vel` |
| robot simulator | Apply commands and simulate sensors | `/cmd_vel` | `/scan`, TF |

## 4. Method

1. Receive a `LaserScan` message.
2. Reject `NaN`, `inf`, and readings outside `range_min`/`range_max`.
3. Inspect three sectors: front (-20° to +20°), left (+20° to +90°), and
   right (-90° to -20°).
4. Find the closest valid measurement in each sector.
5. Use the initial control policy below.

| Condition | Linear velocity | Angular velocity |
| --- | ---: | ---: |
| Front distance >= 0.60 m (or `inf`) | 0.20 m/s | 0.0 rad/s |
| Front distance < 0.60 m; left clearer | 0.0 m/s | +0.60 rad/s |
| Front distance < 0.60 m; right clearer | 0.0 m/s | -0.60 rad/s |

The values are initial parameters to tune during experiments.

## 5. Simulation Environment

Use a differential-drive robot in Gazebo. It should provide `/scan`, `/cmd_vel`, and TF from `base_link` to
`laser_frame`.

Assumptions: the LiDAR scans horizontally; 0° points forward; and the ROS
coordinate convention is x forward, y left, z up.

## 6. Implementation

Planned Python package: `scan_reader_pkg`.

```text
src/scan_reader_pkg/
├── scan_reader_pkg/
│   ├── scan_reader.py           # inspect LaserScan messages
│   └── obstacle_avoidance.py    # reactive controller
├── package.xml
└── setup.py
```

Implementation order:

1. Create the ROS 2 package.
2. Implement `scan_reader`; verify distances in each sector.
3. Implement `obstacle_avoidance`; verify `/cmd_vel` decisions.
4. Connect it to the robot simulator and inspect scans in RViz2.

## 7. Experiments

| ID | Scenario | Expected behaviour |
| --- | --- | --- |
| E1 | No obstacle ahead | Drive forward |
| E2 | Static obstacle in front | Stop and turn toward clearer side |
| E3 | Obstacle left/right only | Keep driving if front is clear |
| E4 | Obstacles on both sides | Drive carefully if front is clear |
| E5 | Invalid/missing scan | Stop safely |

## 8. Results

It works! The robot successfully avoids obstacles just like planned. Overall, a great small project to get my hands dirty with ROS 2 again.

## 9. Failure cases

Nah! It's simple.

## 10. Discussion

Nah.

## 11. Limitations

The first version has no map, localization, global path planner, moving-object
prediction, or recovery behaviour. A reactive controller can get stuck in
complex environments.

## 12. Future works

Next up: Practice SLAM to actually map the environment and play around with Nav2.

## 13. References

- ROS 2 `sensor_msgs/msg/LaserScan` documentation.
- ROS 2 `geometry_msgs/msg/Twist` documentation.
- ROS 2 TF2 and RViz2 documentation.
