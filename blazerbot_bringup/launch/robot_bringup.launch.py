import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    limo_bringup_dir = get_package_share_directory("limo_bringup")

    # 1) Start the official LIMO bringup (base + lidar + etc.)
    limo_start = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(limo_bringup_dir, "launch", "limo_start.launch.py")
        )
    )

    # 2) Gate: wait for 'S', then start wall follower
    arm_and_run = Node(
        package="blazerbot_bringup",
        executable="arm_then_run_wall_follower",
        name="arm_then_run_wall_follower",
        output="screen",
        emulate_tty=True,  # needed to read keyboard input when launched via ros2 launch
    )

    return LaunchDescription([limo_start, arm_and_run])