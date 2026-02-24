evelopment/ros/ros2_ws took 8.6s …
➜ ros2 launch blazerbot_bringup robot_bringup.launch.py                      
[INFO] [launch]: All log files can be found below /home/limo/.ros/log/2026-02-24-23-23-11-897057-ashlimo01-12265
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [limo_base-7]: process started with pid [12339]
[INFO] [ydlidar_ros2_driver_node-8]: process started with pid [12349]
[INFO] [robot_state_publisher-1]: process started with pid [12304]
[INFO] [joint_state_publisher-2]: process started with pid [12306]
[INFO] [static_transform_publisher-3]: process started with pid [12308]
[INFO] [static_transform_publisher-4]: process started with pid [12310]
[INFO] [static_transform_publisher-5]: process started with pid [12312]
[INFO] [static_transform_publisher-6]: process started with pid [12315]
[INFO] [arm_then_run_wall_follower.py-9]: process started with pid [12353]
[static_transform_publisher-3] [WARN] [1771975392.492152200] []: Old-style arguments are deprecated; see --help for new-style arguments
[static_transform_publisher-4] [WARN] [1771975392.491738536] []: Old-style arguments are deprecated; see --help for new-style arguments
[static_transform_publisher-4] [INFO] [1771975392.535524552] [base_link_to_laser_tf]: Spinning until stopped - publishing transform
[static_transform_publisher-4] translation: ('0.180000', '0.000000', '0.000000')
[static_transform_publisher-4] rotation: ('0.000000', '0.000000', '0.000000', '1.000000')
[static_transform_publisher-4] from 'base_link' to 'laser_link'
[static_transform_publisher-5] [WARN] [1771975392.503329544] []: Old-style arguments are deprecated; see --help for new-style arguments
[static_transform_publisher-6] [WARN] [1771975392.525546728] []: Old-style arguments are deprecated; see --help for new-style arguments
[static_transform_publisher-3] [INFO] [1771975392.551464392] [base_footprint_to_base_link_tf]: Spinning until stopped - publishing transform
[static_transform_publisher-3] translation: ('0.000000', '0.000000', '0.150000')
[static_transform_publisher-3] rotation: ('0.000000', '0.000000', '0.000000', '1.000000')
[static_transform_publisher-3] from 'base_footprint' to 'base_link'
[static_transform_publisher-5] [INFO] [1771975392.581955496] [base_link_to_camera_tf]: Spinning until stopped - publishing transform
[static_transform_publisher-5] translation: ('0.180000', '0.000000', '0.180000')
[static_transform_publisher-5] rotation: ('0.000000', '0.000000', '0.000000', '1.000000')
[static_transform_publisher-5] from 'base_link' to 'camera_link'
[static_transform_publisher-6] [INFO] [1771975392.606205512] [base_link_to_imu_tf]: Spinning until stopped - publishing transform
[static_transform_publisher-6] translation: ('0.000000', '0.000000', '0.000000')
[static_transform_publisher-6] rotation: ('0.000000', '0.000000', '0.000000', '1.000000')
[static_transform_publisher-6] from 'base_link' to 'imu_link'
[ydlidar_ros2_driver_node-8] [INFO] [1771975392.629319816] [ydlidar_ros2_driver_node]: [YDLIDAR INFO] Current ROS Driver Version: 1.0.1
[ydlidar_ros2_driver_node-8] 
[ydlidar_ros2_driver_node-8] [YDLIDAR] SDK initializing
[ydlidar_ros2_driver_node-8] [YDLIDAR] SDK has been initialized
[ydlidar_ros2_driver_node-8] [YDLIDAR] SDK Version: 1.2.7
[limo_base-7] Loading parameters: 
[limo_base-7] - port name: ttyTHS1
[limo_base-7] - odom frame name: odom
[limo_base-7] - base frame name: base_link
[limo_base-7] - odom topic name: 1
[limo_base-7] - use_mcnamu_: 0
[limo_base-7] [INFO] [1771975392.667480648] [limo_base]: connet the serial port:'/dev/ttyTHS1'
[limo_base-7] [INFO] [1771975392.670389832] [limo_base]: enableCommandedMode :
[limo_base-7] [INFO] [1771975392.670486312] [limo_base]: Open the serial port:'/dev/ttyTHS1'
[robot_state_publisher-1] Warning: link 'laser_link' material 'laser_material' undefined.
[robot_state_publisher-1]          at line 84 in ./urdf_parser/src/model.cpp
[robot_state_publisher-1] Warning: link 'laser_link' material 'laser_material' undefined.
[robot_state_publisher-1]          at line 84 in ./urdf_parser/src/model.cpp
[robot_state_publisher-1] Warning: link 'depth_camera_link' material 'depth_camera_material' undefined.
[robot_state_publisher-1]          at line 84 in ./urdf_parser/src/model.cpp
[robot_state_publisher-1] Warning: link 'depth_camera_link' material 'depth_camera_material' undefined.
[robot_state_publisher-1]          at line 84 in ./urdf_parser/src/model.cpp
[robot_state_publisher-1] Warning: link 'imu_link' material 'imu_material' undefined.
[robot_state_publisher-1]          at line 84 in ./urdf_parser/src/model.cpp
[robot_state_publisher-1] Warning: link 'imu_link' material 'imu_material' undefined.
[robot_state_publisher-1]          at line 84 in ./urdf_parser/src/model.cpp
[robot_state_publisher-1] [INFO] [1771975392.692019400] [robot_state_publisher]: got segment base_footprint
[robot_state_publisher-1] [INFO] [1771975392.692277480] [robot_state_publisher]: got segment base_link
[robot_state_publisher-1] [INFO] [1771975392.692305000] [robot_state_publisher]: got segment depth_camera_link
[robot_state_publisher-1] [INFO] [1771975392.692317224] [robot_state_publisher]: got segment depth_link
[robot_state_publisher-1] [INFO] [1771975392.692327368] [robot_state_publisher]: got segment front_left_wheel_link
[robot_state_publisher-1] [INFO] [1771975392.692336488] [robot_state_publisher]: got segment front_right_wheel_link
[robot_state_publisher-1] [INFO] [1771975392.692345672] [robot_state_publisher]: got segment imu_link
[robot_state_publisher-1] [INFO] [1771975392.692354216] [robot_state_publisher]: got segment inertial_link
[robot_state_publisher-1] [INFO] [1771975392.692363240] [robot_state_publisher]: got segment laser_link
[robot_state_publisher-1] [INFO] [1771975392.692371528] [robot_state_publisher]: got segment left_steering_hinge
[robot_state_publisher-1] [INFO] [1771975392.692380552] [robot_state_publisher]: got segment rear_left_wheel_link
[robot_state_publisher-1] [INFO] [1771975392.692508072] [robot_state_publisher]: got segment rear_right_wheel_link
[robot_state_publisher-1] [INFO] [1771975392.692528360] [robot_state_publisher]: got segment right_steering_hinge
[ydlidar_ros2_driver_node-8] [YDLIDAR] Lidar successfully connected [/dev/ttyUSB0:230400]
[joint_state_publisher-2] [INFO] [1771975393.270983976] [joint_state_publisher]: Waiting for robot_description to be published on the robot_description topic...
[ydlidar_ros2_driver_node-8] [YDLIDAR] Lidar running correctly! The health status: good
[ydlidar_ros2_driver_node-8] Current Lidar Model Code 151
[ydlidar_ros2_driver_node-8] [YDLIDAR] Baseplate device info
[ydlidar_ros2_driver_node-8] Firmware version: 1.2
[ydlidar_ros2_driver_node-8] Hardware version: 1
[ydlidar_ros2_driver_node-8] Model: Tmini Plus
[ydlidar_ros2_driver_node-8] Serial: 2024092600090187
[ydlidar_ros2_driver_node-8] [YDLIDAR] Current scan frequency: 10.00Hz
[ydlidar_ros2_driver_node-8] [YDLIDAR] Current scan frequency: 10.00Hz
[ydlidar_ros2_driver_node-8] [YDLIDAR] Lidar init success, Elapsed time 1029 ms
[arm_then_run_wall_follower.py-9] Package 'blazerbot_wall_follower' not found
[arm_then_run_wall_follower.py-9] 
[arm_then_run_wall_follower.py-9] [blazerbot_bringup] LIMO is up.
[arm_then_run_wall_follower.py-9] [blazerbot_bringup] Auto-starting wall follower in 2 seconds...
[arm_then_run_wall_follower.py-9] 
[ERROR] [arm_then_run_wall_follower.py-9]: process has died [pid 12353, exit code 1, cmd '/home/limo/development/ros/ros2_ws/install/blazerbot_bringup/lib/blazerbot_bringup/arm_then_run_wall_follower.py --ros-args -r __node:=arm_then_run_wall_follower'].
[ydlidar_ros2_driver_node-8] [YDLIDAR] Create thread 0x9580B8E0
[ydlidar_ros2_driver_node-8] [YDLIDAR] Successed to start scan mode, Elapsed time 2098 ms
[ydlidar_ros2_driver_node-8] [YDLIDAR] Scan Frequency: 10.00Hz
[ydlidar_ros2_driver_node-8] [YDLIDAR] Fixed Size: 400
[ydlidar_ros2_driver_node-8] [YDLIDAR] Sample Rate: 4.00K
[ydlidar_ros2_driver_node-8] [YDLIDAR] Successed to check the lidar, Elapsed time 0 ms
[ydlidar_ros2_driver_node-8] [2026-02-24 23:23:15][info] [YDLIDAR] Now lidar is scanning...
^C[WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
[static_transform_publisher-5] [INFO] [1771975411.039410856] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[INFO] [static_transform_publisher-6]: process has finished cleanly [pid 12315]
[INFO] [static_transform_publisher-5]: process has finished cleanly [pid 12312]
[INFO] [static_transform_publisher-4]: process has finished cleanly [pid 12310]
[INFO] [static_transform_publisher-3]: process has finished cleanly [pid 12308]
[INFO] [robot_state_publisher-1]: process has finished cleanly [pid 12304]
[ERROR] [limo_base-7]: process has died [pid 12339, exit code -6, cmd '/home/limo/development/ros/ros2_ws/install/limo_base/lib/limo_base/limo_base --ros-args --params-file /tmp/launch_params_36dgrg9k'].
[INFO] [joint_state_publisher-2]: process has finished cleanly [pid 12306]
[ydlidar_ros2_driver_node-8] [INFO] [1771975411.039729896] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[ydlidar_ros2_driver_node-8] [INFO] [1771975411.066704424] [ydlidar_ros2_driver_node]: [YDLIDAR INFO] Now YDLIDAR is stopping .......
[limo_base-7] [INFO] [1771975411.040659272] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[limo_base-7] terminate called without an active exception
[static_transform_publisher-6] [INFO] [1771975411.039868744] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[robot_state_publisher-1] [INFO] [1771975411.040672296] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[static_transform_publisher-4] [INFO] [1771975411.042812040] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[static_transform_publisher-3] [INFO] [1771975411.043262408] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[ydlidar_ros2_driver_node-8] [YDLIDAR] Now lidar scanning has stopped!
[INFO] [ydlidar_ros2_driver_node-8]: process has finished cleanly [pid 12349]