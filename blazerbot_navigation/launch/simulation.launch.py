"""
File: simulation.launch.py
Project: Blazerbot Navigation (CS353 Lab 4)
Brief: Master launch file — launches world, robot, SLAM and navigation together
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    desc_pkg = get_package_share_directory('blazerbot_description')
    slam_pkg = get_package_share_directory('blazerbot_slam')
    nav_pkg = get_package_share_directory('blazerbot_navigation')

    # 1. Launch world + robot
    spawn_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(desc_pkg, 'launch', 'spawn.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': 'wall_arena',
            'start_gazebo': 'true',
        }.items()
    )

    # 2. Launch SLAM after 8 seconds
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_pkg, 'launch', 'slam.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )

    # 3. Launch localization after 15 seconds
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'localization.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )

    # 4. Launch navigation after 20 seconds
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'navigation.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),

        spawn_launch,
        TimerAction(period=8.0,  actions=[slam_launch]),
        TimerAction(period=15.0, actions=[localization_launch]),
        TimerAction(period=20.0, actions=[navigation_launch]),
    ])