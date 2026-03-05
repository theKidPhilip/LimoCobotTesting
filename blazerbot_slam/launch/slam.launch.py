"""
File: slam.launch.py
Project: Blazerbot SLAM (CS353 Lab 4)
Brief: Launches slam_toolbox for mapping with Blazerbot
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

    slam_params_file = os.path.join(
        get_package_share_directory('blazerbot_slam'),
        'config',
        'slam_toolbox_params.yaml'
    )

    rviz_config = os.path.join(
        get_package_share_directory('blazerbot_slam'),
        'config',
        'slam_rviz_config.rviz'
    )

    # Use slam_toolbox's own launch file which handles lifecycle correctly
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_file,
        }.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock from Gazebo'
        ),

        DeclareLaunchArgument(
            'use_rviz',
            default_value='false',
            choices=['true', 'false'],
            description='Launch RViz with SLAM config'
        ),

        TimerAction(period=5.0, actions=[slam_launch]),

        rviz_node
    ])