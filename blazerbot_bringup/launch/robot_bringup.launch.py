"""
File: robot_bringup.launch.py
Project: Blazerbot Bringup (CS353 Lab 4)
Brief: Master launch file for the physical Limo robot.
       Supports mapping and navigation modes.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context):

    mode = LaunchConfiguration("mode").perform(context)

    limo_bringup_dir = get_package_share_directory("limo_bringup")
    blazerbot_nav_dir = get_package_share_directory("blazerbot_navigation")
    bringup_dir = get_package_share_directory("blazerbot_bringup")

    limo_slam_params = os.path.join(bringup_dir, "config", "limo_slam_params.yaml")
    limo_nav2_params = os.path.join(bringup_dir, "config", "limo_nav2_params.yaml")

    map_file = os.path.join(bringup_dir, "maps", "limo_map.yaml")

    # Limo base + LIDAR — needed in both modes
    limo_start = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(limo_bringup_dir, "launch", "limo_start.launch.py")
        )
    )

    # ─────────────────────────────────────────────
    # MODE 1: Mapping — build a new map
    # ─────────────────────────────────────────────
    if mode == "mapping":
        slam_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("slam_toolbox"),
                    "launch",
                    "online_async_launch.py",
                )
            ),
            launch_arguments={
                "use_sim_time": "false",
                "slam_params_file": limo_slam_params,
            }.items(),
        )

        return [
            limo_start,
            TimerAction(period=3.0, actions=[slam_launch]),
        ]

    # ─────────────────────────────────────────────
    # MODE 2: Navigation — navigate with saved map
    # ─────────────────────────────────────────────
    elif mode == "navigation":
        localization_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(blazerbot_nav_dir, "launch", "localization.launch.py")
            ),
            launch_arguments={
                "use_sim_time": "false",
                "map_file": map_file,
            }.items(),
        )

        navigation_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(blazerbot_nav_dir, "launch", "navigation.launch.py")
            ),
            launch_arguments={"use_sim_time": "false"}.items(),
        )

        return [
            limo_start,
            TimerAction(period=3.0, actions=[localization_launch]),
            TimerAction(period=8.0, actions=[navigation_launch]),
        ]

    return []


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "mode",
                default_value="mapping",
                choices=["mapping", "navigation"],
                description="mapping: build a new map | navigation: navigate with saved map",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
