[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/LBOJ36UH)



[INFO] Current ROS2 workspace: ros2_ws

limo_ros2 on  testing [!?] on 🐳 v29.1.4 …
➜ ros2 topic list | grep -E "cmd_vel|cmd|twist|drive|steer|wheel"

limo_ros2 …
➜ ros2 topic list | grep -E "cmd_vel"                            
/cmd_vel

limo_ros2 on  testing [!?] …
➜ ros2 topic list                    
/cmd_vel
/imu
/joint_states
/limo_status
/odom
/parameter_events
/robot_description
/rosout
/scan
/tf
/tf_static
/ydlidar_ros2_driver_node/transition_event

limo_ros2 on  testing [!?] on 🐳 v29.1.4 …
➜ ros2 topic info /cmd_vel
Type: geometry_msgs/msg/Twist
Publisher count: 0
Subscription count: 1

limo_ros2 …
➜ ros2 topic info /cmd_vel
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 1

limo_ros2 …
➜ ros2 node info /limo_base
/limo_base
  Subscribers:
    /cmd_vel: geometry_msgs/msg/Twist
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /imu: sensor_msgs/msg/Imu
    /limo_status: limo_msgs/msg/LimoStatus
    /odom: nav_msgs/msg/Odometry
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /tf: tf2_msgs/msg/TFMessage
  Service Servers:
    /limo_base/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /limo_base/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /limo_base/get_parameters: rcl_interfaces/srv/GetParameters
    /limo_base/list_parameters: rcl_interfaces/srv/ListParameters
    /limo_base/set_parameters: rcl_interfaces/srv/SetParameters
    /limo_base/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:


limo_ros2 …
➜ 

limo_ro