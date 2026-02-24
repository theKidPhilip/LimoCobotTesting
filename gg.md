wall_follower-2] Traceback (most recent call last):
[wall_follower-2]   File "/home/limo/development/ros/ros2_ws/install/wall_follower/lib/wall_follower/wall_follower", line 33, in <module>
[wall_follower-2]     sys.exit(load_entry_point('wall-follower==0.0.0', 'console_scripts', 'wall_follower')())
[wall_follower-2]   File "/home/limo/development/ros/ros2_ws/install/wall_follower/lib/wall_follower/wall_follower", line 25, in importlib_load_entry_point
[wall_follower-2]     return next(matches).load()
[wall_follower-2]   File "/usr/lib/python3.10/importlib/metadata/__init__.py", line 171, in load
[wall_follower-2]     module = import_module(match.group('module'))
[wall_follower-2]   File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
[wall_follower-2]     return _bootstrap._gcd_import(name[level:], package, level)
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 992, in _find_and_load_unlocked
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
[wall_follower-2]   File "<frozen importlib._bootstrap>", line 1004, in _find_and_load_unlocked
[wall_follower-2] ModuleNotFoundError: No module named 'wall_follower.scripts'
[ERROR] [wall_follower-2]: process has died [pid 43079, exit code 1, cmd '/home/limo/development/ros/ros2_ws/install/wall_follower/lib/wall_follower/wall_follower --ros-args -r __node:=wall_follower'].
[ydlidar_ros2_driver_node-1] [YDLIDAR] Lidar running correctly! The health status: good
[ydlidar_ros2_driver_node-1] Current Lidar Model Code 151
[ydlidar_ros2_driver_node-1] [YDLIDAR] Baseplate device info
[ydlidar_ros2_driver_node-1] Firmware version: 1.2
[ydlidar_ros2_driver_node-1] Hardware version: 1
[ydlidar_ros2_driver_node-1] Model: Tmini Plus
[ydlidar_ros2_driver_node-1] Serial: 2024092600090187
[ydlidar_ros2_driver_node-1] [YDLIDAR] Current scan frequency: 10.00Hz
[ydlidar_ros2_driver_node-1] [YDLIDAR] Current scan frequency: 10.00Hz
[ydlidar_ros2_driver_node-1] [YDLIDAR] Lidar init success, Elapsed time 965 ms
[ydlidar_ros2_driver_node-1] [YDLIDAR] Create thread 0xA5CBE8E0
[ydlidar_ros2_driver_node-1] [YDLIDAR] Successed to start scan mode, Elapsed time 2097 ms
[ydlidar_ros2_driver_node-1] [YDLIDAR] Scan Frequency: 10.00Hz
[ydlidar_ros2_driver_node-1] [YDLIDAR] Fixed Size: 400
[ydlidar_ros2_driver_node-1] [YDLIDAR] Sample Rate: 4.00K
[ydlidar_ros2_driver_node-1] [YDLIDAR] Successed to check the lidar, Elapsed time 0 ms
[ydlidar_ros2_driver_node-1] [2026-02-24 23:52:19][info] [YDLIDAR] Now lidar is scanning...
^C[WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
[ydlidar_ros2_driver_node-1] [INFO] [1771977164.727051144] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[ydlidar_ros2_driver_node-1] [INFO] [1771977164.781507880] [ydlidar_ros2_driver_node]: [YDLIDAR INFO] Now YDLIDAR is stopping .......
[ydlidar_ros2_driver_node-1] [YDLIDAR] Now lidar scanning has stopped!
[INFO] [ydlidar_ros2_driver_node-1]: process has finished cleanly [pid 43077]
