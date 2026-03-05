"""
File: spawn.launch.py
Project: Blazerbot Description (CS353 Lab 3)
Author: Zabdiel Addo
Version: 1.0.1
Brief:
  Spawn Blazerbot in Gazebo (Ignition/GZ Sim):
   - Optionally starts Gazebo with an ashbot_world .world file
   - Generates SDF from xacro (sim_mode:=true)
   - Spawns robot
   - Starts robot_state_publisher (sim time)
   - Starts ros_gz_bridge using gz_bridge.yaml
   - Optionally starts RViz
"""

import subprocess
import tempfile
from os.path import dirname, join

from ament_index_python.packages import get_package_share_directory
from launch import LaunchContext, LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# CONSTANTS
DESCRIPTION_PKG = "blazerbot_description"
WORLD_PKG = "ashbot_world"  # using ashbot_world for Lab 3
WAIT_PERIOD = 3.0


def write_sdf_from_xacro(description_share: str) -> str:
    """
    Convert blazerbot xacro -> URDF -> SDF and store it in a temporary .sdf file.
    """
    xacro_file = join(description_share, "urdf", "blazerbot.urdf.xacro")

    tmp_urdf = tempfile.NamedTemporaryFile(delete=False, suffix=".urdf")
    tmp_urdf.close()

    tmp_sdf = tempfile.NamedTemporaryFile(delete=False, suffix=".sdf")
    tmp_sdf.close()

    # 1) xacro -> urdf
    with open(tmp_urdf.name, "w", encoding="utf-8") as f_urdf:
        subprocess.run(
            ["xacro", xacro_file, "sim_mode:=true"],
            check=True,
            stdout=f_urdf,
        )

    # 2) urdf -> sdf
    with open(tmp_sdf.name, "w", encoding="utf-8") as f_sdf:
        subprocess.run(
            ["gz", "sdf", "-p", tmp_urdf.name],
            check=True,
            stdout=f_sdf,
        )

    return tmp_sdf.name


def launch_setup(context: LaunchContext) -> list:
    description_share = get_package_share_directory(DESCRIPTION_PKG)
    world_share = get_package_share_directory(WORLD_PKG)

    # Launch args
    world_name = LaunchConfiguration("world").perform(context)
    start_gazebo = LaunchConfiguration("start_gazebo").perform(context)
    rviz_mode = LaunchConfiguration("rviz").perform(context)

    # Spawn pose
    x = LaunchConfiguration("x").perform(context)
    y = LaunchConfiguration("y").perform(context)
    z = LaunchConfiguration("z").perform(context)
    roll = LaunchConfiguration("roll").perform(context)
    pitch = LaunchConfiguration("pitch").perform(context)
    yaw = LaunchConfiguration("yaw").perform(context)

    # Resource path for models

    share_parent = dirname(description_share)

    desc_root = description_share
    desc_meshes = join(description_share, "meshes")
    # optional if you ever add models/
    desc_models = join(description_share, "models")

    world_root = world_share
    world_models = join(world_share, "models")
    world_worlds = join(world_share, "worlds")

    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=(
            f"{share_parent}:"
            f"{desc_root}:{desc_meshes}:{desc_models}:"
            f"{world_root}:{world_models}:{world_worlds}:"
            f"$GZ_SIM_RESOURCE_PATH"
        ),
    )

    # 1) RSP (sim time)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [join(description_share, "launch", "rsp.launch.py")]
        ),
        launch_arguments={
            "sim_mode": "true",
            "use_rviz": "false",  # RViz handled here
        }.items(),
    )

    # 2) Gazebo (optional)
    world_path = join(world_share, "worlds", f"{world_name}.world")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [join(get_package_share_directory("ros_gz_sim"),
                  "launch", "gz_sim.launch.py")]
        ),
        launch_arguments={
            "gz_args": ["-r -v4 ", world_path],
            "on_exit_shutdown": "true",
        }.items(),
    )

    # 3) Spawn robot from generated SDF
    sdf_path = write_sdf_from_xacro(description_share)

    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-file", sdf_path,
            "-name", "blazerbot",
            "-x", str(x),
            "-y", str(y),
            "-z", str(z),
            "-R", str(roll),
            "-P", str(pitch),
            "-Y", str(yaw),
        ],
    )

    # 4) Bridge
    bridge_params = join(description_share, "config", "gz_bridge.yaml")
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        arguments=["--ros-args", "-p", f"config_file:={bridge_params}"],
        parameters=[{"use_sim_time": True}],  # ← add this line
    )

    # 5) RViz (optional)
    launch_nodes = [set_gz_resource_path, rsp, ros_gz_bridge]

    if start_gazebo.lower() == "true":
        spawn_delayed = TimerAction(period=WAIT_PERIOD, actions=[spawn_entity])
        launch_nodes.extend([gazebo, spawn_delayed])
    else:
        launch_nodes.append(spawn_entity)

    if rviz_mode.lower() == "true":
        default_rviz = join(description_share, "rviz", "view_blazerbot.rviz")
        rviz = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", default_rviz],
            parameters=[{"use_sim_time": True}],
        )
        launch_nodes.append(rviz)

    return launch_nodes


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("x", default_value="-1.30",
                                  description="Spawn X (m)"),
            DeclareLaunchArgument("y", default_value="-1.30",
                                  description="Spawn Y (m)"),
            DeclareLaunchArgument("z", default_value="0.10",
                                  description="Spawn Z (m)"),
            DeclareLaunchArgument(
                "roll", default_value="0.0", description="Spawn roll (rad)"),
            DeclareLaunchArgument(
                "pitch", default_value="0.0", description="Spawn pitch (rad)"),
            DeclareLaunchArgument("yaw", default_value="0.0",
                                  description="Spawn yaw (rad)"),
            DeclareLaunchArgument(
                "world",
                default_value="guided_maze",
                description="World name (expects ashbot_world/worlds/<world>.world)",
            ),
            DeclareLaunchArgument(
                "start_gazebo",
                default_value="true",
                choices=["true", "false"],
                description="Start Gazebo from this launch or run Gazebo separately",
            ),
            DeclareLaunchArgument(
                "rviz",
                default_value="false",
                choices=["true", "false"],
                description="Launch RViz if true",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
