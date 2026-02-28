#!/usr/bin/env python3
"""
File: goal_navigator.py
Project: Blazerbot Navigation (CS353 Lab 4)
Brief: Sends predefined navigation goals to Nav2 for autonomous navigation
       in the wall_arena world.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import time


# Predefined goals based on wall_arena layout (3m x 3m arena)
NAVIGATION_GOALS = [
    {"name": "Left Corridor",  "x": -1.0, "y": -1.0, "yaw": 0.0},
    {"name": "Right Corridor", "x":  1.0, "y":  1.0, "yaw": 0.0},
    {"name": "Center",         "x":  0.0, "y":  0.0, "yaw": 0.0},
]


class GoalNavigator(Node):

    def __init__(self):
        super().__init__('goal_navigator')
        self._action_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )
        self.get_logger().info('Goal Navigator node started')

    def send_goal(self, x, y, yaw, name):
        self.get_logger().info(f'Waiting for Nav2 action server...')
        self._action_client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f'Sending goal: {name} -> ({x}, {y})')
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f'Goal {name} was rejected!')
            return False

        self.get_logger().info(f'Goal {name} accepted, navigating...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info(f'Reached: {name}!')
        return True

    def navigate_all_goals(self):
        for goal in NAVIGATION_GOALS:
            success = self.send_goal(
                goal['x'], goal['y'], goal['yaw'], goal['name']
            )
            if success:
                self.get_logger().info(
                    f'Successfully reached {goal["name"]}. Waiting 2s...'
                )
                time.sleep(2.0)
            else:
                self.get_logger().warn(f'Failed to reach {goal["name"]}, skipping...')

        self.get_logger().info('All goals completed!')


def main(args=None):
    rclpy.init(args=args)
    navigator = GoalNavigator()
    navigator.navigate_all_goals()
    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()