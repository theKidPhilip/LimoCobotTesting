#!/usr/bin/env python3
"""
File: goal_navigator.py
Project: Blazerbot Navigation (CS353 Lab 4)

Sends predefined navigation goals to Nav2 using NavigateToPose.

This does NOT interfere with RViz goals:
 - RViz "Nav2 Goal" arrows will still work
 - RViz "2D Pose Estimate" will still work
"""

import math
import time
from typing import List, Dict

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


# -----------------------------------------------------------
# Navigation goals (map frame)
# Adjusted for wall_arena and spawn position (-1.30, -1.30)
# -----------------------------------------------------------
NAVIGATION_GOALS: List[Dict] = [
    # {"name": "Goal 1 - Top Right",    "x":  2.0, "y":  2.0, "yaw": 0.0},
    {"name": "Goal 2 - Bottom Right", "x":  1.5, "y": 1.0, "yaw": 0.2},
    # {"name": "Goal 3 - Left Side",    "x": -1.5, "y":  1.0, "yaw": math.pi / 2},
    {"name": "Goal 4 - Return Home",  "x":  0.0, "y":  0.0, "yaw": 0.0},
]

ACTION_SERVER_TIMEOUT = 30.0
GOAL_TIMEOUT = 180.0


def yaw_to_quaternion(yaw: float):

    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)

    return qz, qw


class GoalNavigator(Node):

    def __init__(self):

        super().__init__("goal_navigator")

        self._client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        self.get_logger().info("Goal Navigator Node started")
        self.get_logger().info("Waiting for Nav2 action server...")

    # -------------------------------------------------

    def wait_for_nav2(self):

        start = time.time()

        while not self._client.wait_for_server(timeout_sec=1.0):

            if time.time() - start > ACTION_SERVER_TIMEOUT:

                self.get_logger().error("Nav2 action server not available")

                return False

            self.get_logger().warn("Still waiting for Nav2...")

        self.get_logger().info("Nav2 action server ready")

        return True

    # -------------------------------------------------

    def build_goal(self, x, y, yaw):

        pose = PoseStamped()

        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        qz, qw = yaw_to_quaternion(yaw)

        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose

    # -------------------------------------------------

    def send_goal(self, name, x, y, yaw):

        goal = NavigateToPose.Goal()

        goal.pose = self.build_goal(x, y, yaw)

        self.get_logger().info(
            f"Sending goal: {name}  ->  x={x:.2f}, y={y:.2f}"
        )

        future = self._client.send_goal_async(goal)

        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error("Goal rejected")

            return False

        self.get_logger().info("Goal accepted")

        result_future = goal_handle.get_result_async()

        start = time.time()

        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.2)

            if result_future.done():

                result = result_future.result()

                status = result.status

                if status == 4:

                    self.get_logger().info(f"SUCCESS: {name}")

                    return True

                else:

                    self.get_logger().warn(
                        f"Goal finished with status {status}"
                    )

                    return False

            if time.time() - start > GOAL_TIMEOUT:

                self.get_logger().error("Goal timeout")

                return False

        return False

    # -------------------------------------------------

    def run_goals(self):

        if not self.wait_for_nav2():

            return

        for g in NAVIGATION_GOALS:

            ok = self.send_goal(g["name"], g["x"], g["y"], g["yaw"])

            if ok:

                self.get_logger().info("Waiting before next goal")

                time.sleep(2)

            else:

                self.get_logger().warn("Continuing to next goal")

                time.sleep(2)

        self.get_logger().info("Finished all goals")



def main(args=None):

    rclpy.init(args=args)

    node = GoalNavigator()

    node.run_goals()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()