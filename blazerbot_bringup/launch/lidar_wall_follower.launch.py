import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # --- 1) Start ONLY the YDLIDAR driver (no limo_base) ---
    ydlidar_dir = get_package_share_directory("ydlidar_ros2_driver")

    lidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ydlidar_dir, "launch", "ydlidar_launch.py")
        ),
        # If your driver uses a different launch name, swap it here.
        # Some setups use: "ydlidar.py" or "ydlidar_launch_view.py"
        # You can also pass params if needed:
        # launch_arguments={"params_file": os.path.join(ydlidar_dir, "params", "TminiPro.yaml")}.items(),
    )

    # --- 2) Start wall follower (AUTO-RUN, publishes /cmd_vel) ---
    wall = Node(
        package="wall_follower",
        executable="wall_follower",
        name="wall_follower",
        output="screen",
        emulate_tty=True,
    )

    return LaunchDescription([lidar, wall])