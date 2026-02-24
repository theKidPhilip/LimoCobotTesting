import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    controller_arg = DeclareLaunchArgument(
        name='controller',
        default_value='basic',
        description='Wall follower controller type: basic | pd | pid'
    )
    controller = LaunchConfiguration('controller')
    
    # 1. THE WORLD
    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory("ashbot_world"),
                    "launch",
                    "world.launch.py",
                )
            ]
        ),
        launch_arguments={"world": "wall_arena"}.items(),
    )

    # 2. THE ROBOT SPAWN
    spawn_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory(
                "blazerbot_description"), "launch", "spawn.launch.py")]
        ),
        # Pass this argument to prevent the double-Gazebo SegFault
        launch_arguments={
            "start_gazebo": "false",
            "rviz": "true",
        }.items()
    )
    # 3. THE WALL FOLLOWER NODE
    wall_follower_node = Node(
        package="wall_follower",       # replace with actual package name
        executable="wall_follower",    # replace with actual entry point
        name="wall_follower",
        output="screen"
    )

    # 3b. PD wall follower
    wall_follower_pd = Node(
        package="wall_follower",
        executable="wall_follower_pd",
        name="wall_follower_pd",
        output="screen",
        condition=IfCondition(
            PythonExpression(["'", controller, "' == 'pd'"])
        ),
    )

    # 3c. PID wall follower
    wall_follower_pid = Node(
        package="wall_follower",
        executable="wall_follower_pid",
        name="wall_follower_pid",
        output="screen",
        condition=IfCondition(
            PythonExpression(["'", controller, "' == 'pid'"])
        ),
    )





    delayed_wall_follower = TimerAction(
        period=7.0, actions=[wall_follower_node, wall_follower_pd, wall_follower_pid])

    # Wait 3 seconds for Gazebo to load before spawning robot
    delayed_spawn = TimerAction(period=3.0, actions=[spawn_launch])

    # Wait for 7 seconds before starting the controllers
    # delayed_controller = TimerAction(period=7.0, actions=[controller_launch])

    return LaunchDescription([controller_arg, world_launch, delayed_spawn, delayed_wall_follower])
