"""
File: localization.launch.py
Project: Blazerbot Navigation (CS353 Lab 4)
Brief: Launches map_server and AMCL for robot localization
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    nav_pkg = get_package_share_directory('blazerbot_navigation')
    slam_pkg = get_package_share_directory('blazerbot_slam')

    map_file = os.path.join(slam_pkg, 'maps', 'wall_arena_map.yaml')

    amcl_params = os.path.join(nav_pkg, 'config', 'amcl_params.yaml')

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),

        # Map server
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'yaml_filename': map_file},
                {'use_transient_local': True}
            ]
        ),

        # AMCL
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                amcl_params,
                {'use_sim_time': use_sim_time}
            ]
        ),

        # Lifecycle manager for localization nodes
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'autostart': True},
                {'node_names': ['map_server', 'amcl']}
            ]
        ),
    ])