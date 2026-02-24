
# Blazerbot Description Package (CS353 Lab 3)

## Overview

This package contains the full URDF/Xacro description of the **Blazerbot**, closely modeled after the AgileX LIMO mobile base.

It includes:

- Robot chassis geometry
- 4-wheel differential drive configuration
- LiDAR sensor definition
- Gazebo simulation plugins
- Launch files for RSP and spawning

This package represents the **physical model** of the robot.

## Package Structure

```
urdf/
├── blazerbot.urdf.xacro          # Main entry point — includes all modules
├── blazerbot_core.xacro          # Core robot body links and joints
├── macros/
│   ├── inertial.xacro            # Inertial property macros
│   ├── material.xacro            # Visual material/color definitions
│   └── wheels_diff_drive.xacro  # Differential drive wheel macros
├── sensors/
│   └── lidar.xacro               # LIDAR sensor definition
├── control/
│   └── gazebo_control.xacro  # Gazebo diff drive plugin config
└── launch/
    ├── rsp.launch.py             # Robot State Publisher launch
    └── spawn.launch.py           # Gazebo spawn launch
```

```
meshes/
└── lidar/
    ├── lidar.dae
    └── lidar.stl
```

```
config/
└── gz_bridge.yaml
```

## Robot Physical Specifications

Based on AgileX LIMO:

- Base Dimensions: 322 × 220 × 251 mm
- Wheelbase: 200 mm
- Track Width: 175 mm
- Ground Clearance: 24 mm
- Base Weight: 4.8 kg

---

## Build Instructions

```bash
cd ~/development/ros/ros2_ws
colcon build --packages-select blazerbot_description
source install/setup.bash
````

---

## Test 1: URDF Validation

```bash
ros2 run xacro xacro \
$(ros2 pkg prefix blazerbot_description)/share/blazerbot_description/urdf/blazerbot.urdf.xacro \
sim_mode:=true > /tmp/blazerbot.urdf
```

---

## Test 2: RViz Only (No Gazebo)

Terminal 1:

```bash
ros2 launch blazerbot_description rsp.launch.py sim_mode:=false
```

Terminal 2:

```bash
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

Terminal 3:

```bash
rviz2
```

Add:

- RobotModel
- TF

---

## Test 3: Full Simulation

### Launch World

```bash
ros2 launch ashbot_world world.launch.py world:=empty
```

### Spawn Robot

```bash
ros2 launch blazerbot_description spawn.launch.py
```

### Test Movement

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.5}, angular: {z: 0.0}}"
```

### Test LiDAR

```bash
ros2 topic echo /scan --once
```

---

## Topics Provided

- `/cmd_vel`
- `/odom`
- `/scan`
- `/joint_states`
- `/tf`

---

## Notes

- `sim_mode=true` enables Gazebo plugins.
- `sim_mode=false` runs pure URDF visualization.
- LiDAR mesh scale can be adjusted inside `lidar.xacro`.
- Wheel dimensions can be adjusted in `blazerbot_core.xacro`.

---

## Authors

Zabdiel Addo
CS353 – Robotics
Ashesi University
