"""
File: rsp.launch.py
Project: Blazerbot Description (CS353 Lab 3)
File Created: Tuesday, 17th February 2026
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: Launch file to start robot_state_publisher for Blazerbot (LIMO AgileX).
       Expands xacro -> URDF and publishes it to /robot_description, then publishes TF.
-----
Last Modified: Tuesday, 17th February 2026 12:52:09 AM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo.
"""

from os.path import join

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

PACKAGE_NAME = "blazerbot_description"


def launch_setup(context):
    """
    Expands xacro -> URDF and publishes it to the /robot_description parameter,
    then starts robot_state_publisher to publish TF frames.

    If sim_mode := true:
      - We do NOT start joint_state_publisher (Gazebo publishes joint states).
    If sim_mode := false:
      - We start joint_state_publisher so RViz can animate joints.
    """

    pkg_share = FindPackageShare(package=PACKAGE_NAME).find(PACKAGE_NAME)

    sim_mode = LaunchConfiguration("sim_mode").perform(context)
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    rviz_config = LaunchConfiguration("rviz_config").perform(context)

    xacro_file = join(pkg_share, "urdf", "blazerbot.urdf.xacro")

    # Only arg needed for Lab 3: sim_mode
    robot_description_cmd = Command(
        [
            "xacro ",
            xacro_file,
            " ",
            "sim_mode:=",
            sim_mode,
        ]
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": ParameterValue(robot_description_cmd, value_type=str),
                "use_sim_time": sim_mode.lower() == "true",
            }
        ],
    )

    # In simulation, Gazebo + JointStatePublisher plugin handles joint states
    if sim_mode.lower() == "true":
        # RViz optional
        if use_rviz.lower() == "true":
            rviz_node = Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", rviz_config],
                parameters=[{"use_sim_time": True}],
            )
            return [robot_state_publisher, rviz_node]

        return [robot_state_publisher]

    # Not sim: publish joint states locally for RViz
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
    )

    if use_rviz.lower() == "true":
        rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
            parameters=[{"use_sim_time": False}],
        )
        return [joint_state_publisher, robot_state_publisher, rviz_node]

    return [joint_state_publisher, robot_state_publisher]


def generate_launch_description():
    pkg_share = FindPackageShare(package=PACKAGE_NAME).find(PACKAGE_NAME)

    # Update this to whatever RViz config you actually have.
    # If you don't have one yet, you can create rviz/blazerbot.rviz later.
    default_rviz_config = join(pkg_share, "rviz", "blazerbot.rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "sim_mode",
                default_value="true",
                choices=["true", "false"],
                description="Use simulated time if true (gz-sim).",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="false",
                choices=["true", "false"],
                description="Start RViz automatically if true.",
            ),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=default_rviz_config,
                description="Full path to the RViz config file.",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
