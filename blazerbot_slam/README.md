
# Blazerbot SLAM Package (CS353 Lab 4)

## Overview

This package handles **Simultaneous Localization and Mapping (SLAM)** for the Blazerbot robot using the `slam_toolbox` library. It subscribes to the robot's LIDAR data and odometry to build a 2D occupancy grid map of the environment in real time.

Once the environment has been fully explored, the generated map is saved as `.pgm` and `.yaml` files for use by the navigation stack.

## Package Structure

```

blazerbot_slam/
├── config/
│   ├── slam_toolbox_params.yaml    # SLAM toolbox configuration
│   └── slam_rviz_config.rviz       # RViz config for visualizing SLAM
├── launch/
│   └── slam.launch.py              # Main SLAM launch file
├── CMakeLists.txt
├── package.xml
└── README.md

```

## Dependencies

- `slam_toolbox`
- `nav2_map_server`
- `robot_state_publisher`

Install if missing:

```bash
sudo apt-get install ros-jazzy-slam-toolbox ros-jazzy-nav2-map-server
```

## How It Works

1. Subscribes to `/scan` (LIDAR) and `/odom` (odometry)
2. Fuses sensor data using scan matching to build a live occupancy grid
3. Publishes the map on `/map` and the `map → odom` TF transform
4. Map updates every 5 seconds as the robot explores
5. Once exploration is complete, the map is saved to the `maps/` folder

## Build

```bash
colcon build --packages-select blazerbot_slam --symlink-install
source install/setup.zsh
```

## Usage

### Step 1 — Launch simulation first

```bash
ros2 launch blazerbot_description spawn.launch.py
```

### Step 2 — Launch SLAM

```bash
# Without RViz
ros2 launch blazerbot_slam slam.launch.py

# With RViz
ros2 launch blazerbot_slam slam.launch.py use_rviz:=true
```

### Step 3 — Drive the robot to build the map

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

| Key | Action |
|-----|--------|
| `i` | Forward |
| `,` | Reverse |
| `j` | Turn left |
| `l` | Turn right |
| `k` | Stop |
| `w/x` | Increase/decrease linear speed |
| `q/z` | Increase/decrease all speeds |

Drive slowly and cover the entire environment, going along every wall and into every corner.

### Step 4 — Save the map

From the RViz SlamToolboxPlugin panel, type the full path and click **Save Map**:

```
/home/ubuntu/development/ros/ros2_ws/src/lab-4-navigation-limo-blazers/maps/blazerbot_map
```

Or via terminal:

```bash
ros2 run nav2_map_server map_saver_cli -f maps/blazerbot_map --ros-args -p use_sim_time:=true
```

This generates two files in the `maps/` folder:

- `blazerbot_map.pgm` — the map image
- `blazerbot_map.yaml` — map metadata (resolution, origin)

## Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/scan` | `sensor_msgs/msg/LaserScan` | Subscribed |
| `/odom` | `nav_msgs/msg/Odometry` | Subscribed |
| `/map` | `nav_msgs/msg/OccupancyGrid` | Published |
| `/tf` | `tf2_msgs/msg/TFMessage` | Published |

## Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `base_frame` | `base_link` | Robot base frame |
| `odom_frame` | `odom` | Odometry frame |
| `map_frame` | `map` | Map frame |
| `scan_topic` | `/scan` | LIDAR topic |
| `resolution` | `0.05` | Map resolution in meters/cell |
| `max_laser_range` | `6.0` | Max LIDAR range in meters |
| `map_update_interval` | `5.0` | Seconds between map updates |

## Authors

Zabdiel Addo, Philip Quartey
CS353 – Introduction to AI Robotics
Ashesi University

