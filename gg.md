
limo_ros2 on  testing [!?] took 7.5s …
➜ ros2 topic echo /map_updates --once
^C%                                               

limo_ros2 took 6m 8.1s …
➜ ros2 topic list | grep map         
/map
/map_metadata
/map_updates

limo_ros2 …
➜ ros2 topic hz /map        
^C%                                               

limo_ros2 on  testing [!?] took 43.2s …
➜ ros2 run tf2_ros tf2_echo map base_footprint
[INFO] [1772292267.559346918] [tf2_echo]: Waiting for transform map ->  base_footprint: Invalid frame ID "map" passed to canTransform argument target_frame - frame does not exist
[INFO] [1772292269.490778768] [tf2_echo]: Waiting for transform map ->  base_footprint: Invalid frame ID "map" passed to canTransform argument target_frame - frame does not exist
[INFO] [1772292270.490817193] [tf2_echo]: Waiting for transform map ->  base_footprint: Could not find a connection between 'map' and 'base_footprint' because they are not part of the same tree.Tf has two or more unconnected trees.
[INFO] [1772292271.490823832] [tf2_echo]: Waiting for transform map ->  base_footprint: Could not find a connection between 'map' and 'base_footprint' because they are not part of the same tree.Tf has two or more unconnected trees.
[INFO] [1772292273.490781254] [tf2_echo]: Waiting for transform map ->  base_footprint: Could not find a connection between 'map' and 'base_footprint' because they are not part of the same tree.Tf has two or more unconnected trees.
^C[INFO] [1772292274.245656408] [rclcpp]: signal_handler(SIGINT/SIGTERM)

limo_ros2 took 7.5s …
➜ ros2 lifecycle list slam_toolbox                                   
Node not found

limo_ros2 on  testing [!?] …
➜ 

limo_ros2 …
➜ 