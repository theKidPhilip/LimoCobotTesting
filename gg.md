import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
#from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    rf2o_dir = get_package_share_directory('rf2o_laser_odometry')
    limo_description_dir = get_package_share_directory('limo_description')
    ydlidar_ros_dir = get_package_share_directory("ydlidar_ros2_driver")
    limo_base_dir = get_package_share_directory('limo_base')
    # limo_bringup_dir = get_package_share_directory('limo_bringup')
    # limo_gazebo = get_package_share_directory('limo_car')

    # URDF
    urdf_file = os.path.join(limo_description_dir, 'urdf', 'limo_four_diff.xacro')
    robot_description = Command(['xacro ', urdf_file])
    
    # Nodes
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
            }]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    # static TFs
    base_footprint_to_base_link_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_base_link_tf',
        arguments=['0', '0', '0.15', '0', '0', '0', 'base_footprint', 'base_link'],
        output='screen'
    )

    base_link_to_laser_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_laser_tf',
        arguments=['0.18','0','0.0','0','0','0','1','base_link','laser_link'],
        output='screen'
    )
    
    base_link_to_camera_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_camera_tf',
        arguments=['0.18','0','0.18','0','0','0','1','base_link','camera_link'],
        output='screen'
    )
    
    base_link_to_imu_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_imu_tf',
        arguments=['0','0','0','0','0','0','1','base_link','imu_link'],
        output='screen'
    )
    
    ld = LaunchDescription()
    # publish URDF and joint states first
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(base_footprint_to_base_link_tf)

    # Add static transforms
    ld.add_action(base_link_to_laser_tf_node)
    ld.add_action(base_link_to_camera_tf_node)
    ld.add_action(base_link_to_imu_tf_node)

    # Include limo_base
    ld.add_action(
    	IncludeLaunchDescription(
    	    PythonLaunchDescriptionSource([limo_base_dir, '/launch', '/limo_base.launch.py'])
    	)
    )
    
    # Include YDLIDAR driver
    ld.add_action(
    	IncludeLaunchDescription(
    	    PythonLaunchDescriptionSource([ydlidar_ros_dir, '/launch', '/ydlidar_launch.py'])
    	)
    )

    return ld



development/ros/ros2_ws took 32.2s …
✦ ➜ ros2 node list                                       

development/ros/ros2_ws …
✦ ➜ ros2 node list
/base_footprint_to_base_link_tf
/base_link_to_camera_tf
/base_link_to_imu_tf
/base_link_to_laser_tf
/joint_state_publisher
/launch_ros_78172
/limo_base
/robot_state_publisher
/wall_follower
/ydlidar_ros2_driver_node

development/ros/ros2_ws …
✦ ➜ ros2 param list /limo_base                                              
  base_frame
  control_rate
  odom_frame
  port_name
  pub_odom_tf
  qos_overrides./parameter_events.publisher.depth
  qos_overrides./parameter_events.publisher.durability
  qos_overrides./parameter_events.publisher.history
  qos_overrides./parameter_events.publisher.reliability
  qos_overrides./tf.publisher.depth
  qos_overrides./tf.publisher.durability
  qos_overrides./tf.publisher.history
  qos_overrides./tf.publisher.reliability
  use_mcnamu
  use_sim_time

development/ros/ros2_ws took 4.7s …
✦ ➜ ros2 service list         
/base_footprint_to_base_link_tf/describe_parameters
/base_footprint_to_base_link_tf/get_parameter_types
/base_footprint_to_base_link_tf/get_parameters
/base_footprint_to_base_link_tf/list_parameters
/base_footprint_to_base_link_tf/set_parameters
/base_footprint_to_base_link_tf/set_parameters_atomically
/base_link_to_camera_tf/describe_parameters
/base_link_to_camera_tf/get_parameter_types
/base_link_to_camera_tf/get_parameters
/base_link_to_camera_tf/list_parameters
/base_link_to_camera_tf/set_parameters
/base_link_to_camera_tf/set_parameters_atomically
/base_link_to_imu_tf/describe_parameters
/base_link_to_imu_tf/get_parameter_types
/base_link_to_imu_tf/get_parameters
/base_link_to_imu_tf/list_parameters
/base_link_to_imu_tf/set_parameters
/base_link_to_imu_tf/set_parameters_atomically
/base_link_to_laser_tf/describe_parameters
/base_link_to_laser_tf/get_parameter_types
/base_link_to_laser_tf/get_parameters
/base_link_to_laser_tf/list_parameters
/base_link_to_laser_tf/set_parameters
/base_link_to_laser_tf/set_parameters_atomically
/joint_state_publisher/describe_parameters
/joint_state_publisher/get_parameter_types
/joint_state_publisher/get_parameters
/joint_state_publisher/list_parameters
/joint_state_publisher/set_parameters
/joint_state_publisher/set_parameters_atomically
/launch_ros_78172/describe_parameters
/launch_ros_78172/get_parameter_types
/launch_ros_78172/get_parameters
/launch_ros_78172/list_parameters
/launch_ros_78172/set_parameters
/launch_ros_78172/set_parameters_atomically
/limo_base/describe_parameters
/limo_base/get_parameter_types
/limo_base/get_parameters
/limo_base/list_parameters
/limo_base/set_parameters
/limo_base/set_parameters_atomically
/robot_state_publisher/describe_parameters
/robot_state_publisher/get_parameter_types
/robot_state_publisher/get_parameters
/robot_state_publisher/list_parameters
/robot_state_publisher/set_parameters
/robot_state_publisher/set_parameters_atomically
/start_scan
/stop_scan
/wall_follower/describe_parameters
/wall_follower/get_parameter_types
/wall_follower/get_parameters
/wall_follower/list_parameters
/wall_follower/set_parameters
/wall_follower/set_parameters_atomically
/ydlidar_ros2_driver_node/change_state
/ydlidar_ros2_driver_node/describe_parameters
/ydlidar_ros2_driver_node/get_parameter_types
/ydlidar_ros2_driver_node/get_parameters
/ydlidar_ros2_driver_node/list_parameters
/ydlidar_ros2_driver_node/set_parameters
/ydlidar_ros2_driver_node/set_parameters_atomically

development/ros/ros2_ws …
✦ ➜ 