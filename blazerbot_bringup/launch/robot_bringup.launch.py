"""
File: robot_bringup.launch.py
Project: lab-3-locomotion-and-sensing-limo-blazers
File Created: Tuesday, 24th February 2026 10:09:32 PM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 24th February 2026 10:09:44 PM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""

"""
Real robot bringup:
  1) Launch all required nodes for the LIMO robot (via limo_bringup)
  2) Run wall follower ONLY after user presses 'S'
"""

from os.path import join

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # 1) LIMO robot stack (base + lidar + tf etc.)
    # From your screenshot, the file is: limo_bringup/launch/limo_start.launch.py
    limo_start = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(
                get_package_share_directory("limo_bringup"),
                "launch",
                "limo_start.launch.py",
            )
        )
    )

    # 2) Gate: wait for 'S' then start the wall follower
    arm_and_run = Node(
        package="blazerbot_bringup",
        executable="arm_then_run_wall_follower.py",
        name="arm_then_run_wall_follower",
        output="screen",
    )

    return LaunchDescription([limo_start, arm_and_run])