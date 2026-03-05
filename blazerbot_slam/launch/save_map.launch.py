import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# Your repo map folder (fixed path as you provided)
MAP_DIR = "/home/ubuntu/development/ros/ros2_ws/src/lab-4-navigation-limo-blazers/blazerbot_slam/maps"


def generate_launch_description():
    map_name = LaunchConfiguration("map_name")

    def launch_setup(context, *args, **kwargs):
        os.makedirs(MAP_DIR, exist_ok=True)

        # map_saver_cli expects a prefix without extension
        map_prefix = os.path.join(MAP_DIR, map_name.perform(context))

        map_saver = Node(
            package="nav2_map_server",
            executable="map_saver_cli",
            name="map_saver",
            output="screen",
            arguments=[
                "-f", map_prefix,
                "--ros-args",
                "-p", "save_map_timeout:=5.0"  # float for Jazzy
            ],
        )

        return [map_saver]

    return LaunchDescription([
        DeclareLaunchArgument(
            "map_name",
            default_value="wall_arena_map",
            description="Name of the map to save (no extension)"
        ),
        OpaqueFunction(function=launch_setup),
    ])