# Blazerbot Navigation Package (CS353 Lab 4)

## Overview

This package implements **autonomous navigation** for the Blazerbot robot using the ROS2 Navigation Stack (Nav2). It uses **AMCL (Adaptive Monte Carlo Localization)** to localize the robot within a pre-built map, and the **Nav2 stack** for path planning and obstacle avoidance.

The robot autonomously navigates to predefined goals within the `wall_arena` Gazebo world without colliding with obstacles.

## Package Structure

```
blazerbot_navigation/
├── config/
│   ├── amcl_params.yaml          # AMCL localization configuration
│   ├── nav2_params.yaml          # Full Nav2 stack configuration
│   └── nav_rviz_config.rviz      # RViz config for navigation visualization
├── launch/
│   ├── localization.launch.py    # Launches map_server and AMCL
│   ├── navigation.launch.py      # Launches full Nav2 stack
│   └── simulation.launch.py     # Master launch — world + robot + SLAM + Nav2
├── scripts/
│   └── goal_navigator.py         # Sends predefined goals to Nav2
├── maps/
├── CMakeLists.txt
├── package.xml
└── README.md
```

## Dependencies

- `nav2_bringup`
- `nav2_amcl`
- `nav2_map_server`
- `nav2_bt_navigator`
- `nav2_planner`
- `nav2_controller`
- `nav2_behaviors`
- `nav2_lifecycle_manager`

Install if missing:

```bash
sudo apt-get install ros-jazzy-navigation2 ros-jazzy-nav2-bringup
```

## How It Works

### Localization (AMCL)

- Loads the pre-built map from the `maps/` folder
- Uses particle filter to estimate the robot's position within the map
- Publishes the `map → odom` transform
- Initial pose is set to `(0, 0, 0)` — the robot spawn point

### Navigation (Nav2)

- **Planner Server** — computes a global path from current position to goal using NavFn
- **Controller Server** — follows the global path using DWB local planner
- **Behavior Server** — handles recovery behaviors (spin, wait)
- **BT Navigator** — orchestrates the full navigation using behavior trees

### Goal Navigator Script

Sends three predefined goals autonomously:

| Goal | X | Y | Description |
|------|---|---|-------------|
| Left Corridor | -1.0 | -1.0 | Left side of arena |
| Right Corridor | 1.0 | 1.0 | Right side of arena |
| Center | 0.0 | 0.0 | Center of arena |

## Build

```bash
colcon build --packages-select blazerbot_navigation --symlink-install
source install/setup.bash
```

## Usage

### Full Simulation Launch (Recommended)

Launches everything in one command — world, robot, SLAM and Nav2:

```bash
ros2 launch blazerbot_navigation simulation.launch.py
```

Wait ~20 seconds for all nodes to initialize, then run the goal navigator:

```bash
ros2 run blazerbot_navigation goal_navigator.py
```

### Individual Launch Files

**Localization only:**

```bash
ros2 launch blazerbot_navigation localization.launch.py
```

**Navigation stack only:**

```bash
ros2 launch blazerbot_navigation navigation.launch.py
```

### Sending Goals Manually via RViz

1. Open RViz with the nav config
2. Set fixed frame to `map`
3. Click **Nav2 Goal** button in the toolbar
4. Click anywhere on the map to send a goal

### Sending Goals via Terminal

```bash
ros2 topic pub /goal_pose geometry_msgs/msg/PoseStamped \
"{header: {frame_id: 'map'}, pose: {position: {x: 0.5, y: 0.5, z: 0.0}, orientation: {w: 1.0}}}" --once
```

## Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/map` | `nav_msgs/msg/OccupancyGrid` | Static map from map_server |
| `/amcl_pose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | Robot estimated pose |
| `/particle_cloud` | `nav2_msgs/msg/ParticleCloud` | AMCL particles |
| `/plan` | `nav_msgs/msg/Path` | Global planned path |
| `/local_plan` | `nav_msgs/msg/Path` | Local planned path |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Velocity commands to robot |
| `/scan` | `sensor_msgs/msg/LaserScan` | LIDAR data for obstacle avoidance |

## Key Parameters

### AMCL

| Parameter | Value | Description |
|-----------|-------|-------------|
| `min_particles` | `500` | Minimum particle count |
| `max_particles` | `2000` | Maximum particle count |
| `base_frame_id` | `base_link` | Robot base frame |
| `laser_model_type` | `likelihood_field` | Laser sensor model |

### Nav2

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_vel_x` | `0.26` | Maximum linear velocity |
| `max_vel_theta` | `1.0` | Maximum angular velocity |
| `xy_goal_tolerance` | `0.25` | Goal position tolerance (m) |
| `yaw_goal_tolerance` | `0.25` | Goal orientation tolerance (rad) |
| `inflation_radius` | `0.55` | Obstacle inflation radius |

## Navigation Stack Architecture

```
goal_navigator.py
      ↓
/navigate_to_pose (action)
      ↓
bt_navigator (behavior tree)
      ↓
planner_server ──→ global path ──→ controller_server ──→ /cmd_vel
      ↑                                    ↑
global_costmap                      local_costmap
      ↑                                    ↑
    /map                                /scan
```

## Troubleshooting

**Robot not moving:**

```bash
ros2 lifecycle list bt_navigator  # Should show active
ros2 action list                  # Should show /navigate_to_pose
```

**Goals outside map bounds:**

- Remap the environment using `blazerbot_slam`
- Check `maps/blazerbot_map.yaml` for map dimensions

**AMCL not localizing:**

```bash
ros2 topic hz /amcl_pose  # Should be publishing
ros2 topic hz /scan       # Should be ~5-10Hz
```

## Authors

Zabdiel Addo, Philip Quartey
CS353 – Introduction to AI Robotics
Ashesi University
