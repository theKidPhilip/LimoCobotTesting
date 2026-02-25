import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # If you're using the official limo_bringup launch:
    limo_bringup_dir = get_package_share_directory("limo_bringup")

    limo_start = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(limo_bringup_dir, "launch", "limo_start.launch.py")
        )
    )

    wall_follower_node = Node(
        package="wall_follower",
        executable="wall_follower",   # console script name
        name="wall_follower",
        output="screen",
        emulate_tty=True,
    )

    return LaunchDescription([
        limo_start,
        wall_follower_node
    ])