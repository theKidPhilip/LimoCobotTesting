# Blazerbot Navigation Package (CS353 Lab 4)

## Overview

This package implements **autonomous navigation** for the Blazerbot robot using the ROS2 Navigation Stack (Nav2). It uses:

- **AMCL (Adaptive Monte Carlo Localization)** to localize the robot within a **saved map**
- The **Nav2 stack** for **path planning**, **path following**, and **obstacle avoidance**
- A helper script (`goal_navigator.py`) to send predefined goals automatically

You can also send goals manually in RViz using the **Nav2 Goal** arrow tool.

---

## Package Structure

```

blazerbot_navigation/
├── config/
│   ├── amcl_params.yaml          # AMCL localization configuration
│   ├── nav2_params.yaml          # Full Nav2 stack configuration
│   └── nav_rviz_config.rviz      # RViz config for navigation visualization
├── launch/
│   ├── localization.launch.py    # Launches map_server + AMCL
│   ├── navigation.launch.py      # Launches full Nav2 stack
│   └── simulation.launch.py      # Master launch (mode:=slam OR mode:=nav)
├── scripts/
│   └── goal_navigator.py         # Sends predefined goals to Nav2
├── maps/
│   ├── blazerbot_map.yaml        # Saved map metadata
│   └── blazerbot_map.pgm         # Saved map image
├── CMakeLists.txt
├── package.xml
└── README.md

````

---

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
````

---

## How It Works

### 1) Localization (AMCL)

* Loads a **saved map** from `maps/`
* Uses a particle filter to estimate the robot’s pose inside the map
* Publishes the `map → odom` transform
* Publishes estimated pose on `/amcl_pose`

### 2) Navigation (Nav2)

* **Planner Server** computes a global path from current pose to the goal (`/plan`)
* **Controller Server** follows that path by publishing velocity commands (`/cmd_vel`)
* **Behavior Server** runs recovery behaviors (spin, back up, wait)
* **BT Navigator** coordinates everything with a behavior tree

### 3) Goal Sending Options

You have two options:

#### A) RViz Goal Arrow (Manual)

* Use the **Nav2 Goal** tool in RViz
* Click on the map and drag an arrow to set the goal direction (yaw)

#### B) `goal_navigator.py` (Automatic)

* Sends a list of predefined goals using the `NavigateToPose` action
* Useful for demos and repeatable testing

---

## Build

```bash
colcon build --packages-select blazerbot_navigation --symlink-install
source install/setup.bash
```

---

## Usage

### Option 1 — Build/Update Map (SLAM Mode)

This launches Gazebo + robot + SLAM (mapping). Use this only when generating a map.

```bash
ros2 launch blazerbot_navigation simulation.launch.py mode:=slam
```

Drive the robot around to explore, then save the map (using SLAM toolbox plugin or map_saver).

> After saving, ensure the map files are in:
>
> `blazerbot_navigation/maps/blazerbot_map.yaml`
> `blazerbot_navigation/maps/blazerbot_map.pgm`

---

### Option 2 — Navigate Using Saved Map (Nav Mode)

This launches Gazebo + robot + **map_server + AMCL + Nav2** (navigation).

```bash
ros2 launch blazerbot_navigation simulation.launch.py mode:=nav
```

#### Send a goal using RViz (recommended demo)

1. Open RViz using `nav_rviz_config.rviz`
2. Set Fixed Frame to `map`
3. Click **2D Pose Estimate** and set the robot’s initial pose
4. Click **Nav2 Goal**, then click-and-drag the arrow to a destination

#### Send goals automatically (goal_navigator script)

```bash
ros2 run blazerbot_navigation goal_navigator.py
```

---

## Individual Launch Files

### Localization only (map_server + AMCL)

```bash
ros2 launch blazerbot_navigation localization.launch.py
```

### Navigation stack only (planner/controller/BT)

```bash
ros2 launch blazerbot_navigation navigation.launch.py
```

---

## Topics

| Topic             | Type                                          | Description              |
| ----------------- | --------------------------------------------- | ------------------------ |
| `/map`            | `nav_msgs/msg/OccupancyGrid`                  | Static map (map_server)  |
| `/amcl_pose`      | `geometry_msgs/msg/PoseWithCovarianceStamped` | Robot estimated pose     |
| `/particle_cloud` | `nav2_msgs/msg/ParticleCloud`                 | AMCL particles           |
| `/plan`           | `nav_msgs/msg/Path`                           | Global path from planner |
| `/cmd_vel`        | `geometry_msgs/msg/Twist`                     | Velocity commands        |
| `/scan`           | `sensor_msgs/msg/LaserScan`                   | LIDAR data for obstacles |

---

## Quick Verification Commands

Check Nav2 action exists:

```bash
ros2 action list | grep navigate
```

Check robot is being commanded during navigation:

```bash
ros2 topic hz /cmd_vel
```

Check AMCL is publishing pose:

```bash
ros2 topic hz /amcl_pose
```

---

## Troubleshooting

### Robot not moving

* Ensure Nav2 nodes are ACTIVE:

```bash
ros2 lifecycle list
```

* Ensure `/cmd_vel` publishes when a goal is sent:

```bash
ros2 topic hz /cmd_vel
```

### AMCL not localizing

* In RViz, always set **2D Pose Estimate** once before sending a Nav2 Goal.
* Check `/scan` and `/amcl_pose` frequency:

```bash
ros2 topic hz /scan
ros2 topic hz /amcl_pose
```

### Goal rejected

* Confirm the goal is within the map bounds.
* Confirm TF is healthy: `map → odom → base_link → laser_link`

---

## Authors

Zabdiel Addo, Philip Quartey
CS353 – Introduction to AI Robotics
Ashesi University


