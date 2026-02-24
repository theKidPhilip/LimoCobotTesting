[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/LBOJ36UH)


chmod +x blazerbot_bringup/scripts/arm_then_run_wall_follower.py


) Run it on the robot (inside the robot’s environment)

From the robot workspace:

cd ~/development/ros/ros2_ws
colcon build --packages-select blazerbot_bringup
source install/setup.bash

Then run:

export ROS_DOMAIN_ID=41
ros2 launch blazerbot_bringup robot_bringup.launch.py

You’ll see the prompt. Press S and the robot begins wall following.

Quick sanity checks (before pressing S)

Open another robot terminal:

export ROS_DOMAIN_ID=41
ros2 topic echo /scan --once

If /scan prints, you’re good.
