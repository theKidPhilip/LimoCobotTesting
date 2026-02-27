#!/usr/bin/env python3
# File: wall_follower_node.py
# Package: blazerbot_wall_follower
# Node: wall_follower_node
#
# Purpose:
#   ROS2 PD wall follower using LaserScan on 'scan' and publishing Twist on 'cmd_vel'.
#   Works for differential-drive robots.

import math
import time
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


def clamp(value: float, low: float, high: float) -> float:
    """Limit 'value' so it never goes below low or above high."""
    return max(low, min(value, high))


def sanitize_range(r: float, range_min: float, range_max: float) -> float:
    """
    Clean up LiDAR readings:
      - inf / NaN / <= 0  -> treat as range_max (meaning 'no obstacle close')
      - below range_min   -> range_min
      - above range_max   -> range_max
    """
    if math.isinf(r) or math.isnan(r) or r <= 0.0:
        return range_max
    if r < range_min:
        return range_min
    if r > range_max:
        return range_max
    return r


class WallFollowerNode(Node):
    def __init__(self) -> None:
        super().__init__("wall_follower_node")

        #  Parameters
        # Wall-following goal
        self.declare_parameter("wall_distance", 0.5)      # meters
        self.declare_parameter("safety_distance", 0.35)   # meters
        self.declare_parameter("linear_speed", 0.25)      # m/s

        # PD gains
        self.declare_parameter("kp", 1.2)
        self.declare_parameter("kd", 0.15)

        # Safety + limits
        self.declare_parameter("max_angular_speed", 1.2)  # rad/s
        self.declare_parameter("follow_side", "right")    # "right" or "left"

        # Angle windows for sampling scan (degrees)
        self.declare_parameter("front_deg", 0.0)
        self.declare_parameter("front_right_deg", -45.0)
        self.declare_parameter("right_deg", -90.0)
        self.declare_parameter("window_half_width_deg", 10.0)

        # Type-safe parameter getters
        # These remove the "Unknown | None" static type error from editors.
        def get_param_float(name: str) -> float:
            value = self.get_parameter(name).value
            if value is None:
                raise ValueError(f"Parameter '{name}' is None")
            return float(value)

        def get_param_str(name: str) -> str:
            value = self.get_parameter(name).value
            if value is None:
                raise ValueError(f"Parameter '{name}' is None")
            return str(value)

        # Read parameters (type-safe)
        self.wall_distance = get_param_float("wall_distance")
        self.safety_distance = get_param_float("safety_distance")
        self.linear_speed = get_param_float("linear_speed")

        self.kp = get_param_float("kp")
        self.kd = get_param_float("kd")

        self.max_angular_speed = get_param_float("max_angular_speed")
        self.follow_side = get_param_str("follow_side").lower().strip()

        self.front_deg = get_param_float("front_deg")
        self.front_right_deg = get_param_float("front_right_deg")
        self.right_deg = get_param_float("right_deg")
        self.window_half_width_deg = get_param_float("window_half_width_deg")

        # Validate follow_side
        if self.follow_side not in ("right", "left"):
            self.get_logger().warn(
                "follow_side must be 'right' or 'left'. Defaulting to 'right'."
            )
            self.follow_side = "right"

        # If following LEFT wall, mirror the right-side angles
        if self.follow_side == "left":
            self.front_right_deg = +abs(self.front_right_deg)
            self.right_deg = +abs(self.right_deg)

        # ROS interfaces
        self.scan_sub = self.create_subscription(
            LaserScan, "scan", self.scan_callback, 10
        )
        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)

        #  Controller state
        self.latest_scan: Optional[LaserScan] = None
        self.last_error: float = 0.0
        self.last_time: Optional[float] = None

        # Run control loop at 10 Hz (every 0.1 s)
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info(
            f"WallFollowerNode started. side={self.follow_side}, wall_distance={self.wall_distance}, "
            f"kp={self.kp}, kd={self.kd}"
        )

    def scan_callback(self, msg: LaserScan) -> None:
        """Store the latest scan so the timer loop can use it."""
        self.latest_scan = msg

    def control_loop(self) -> None:
        """
        Main loop:
          1) Read distances from scan (front, front-right, right/left)
          2) If front obstacle too close -> stop + turn away (safety)
          3) Else PD control to keep desired wall distance
          4) Publish cmd_vel
        """
        if self.latest_scan is None:
            return  # don’t drive until scan exists

        scan = self.latest_scan

        # Read key distances using angle windows
        front = self.get_min_range_in_window(
            scan, self.front_deg, self.window_half_width_deg)
        side = self.get_min_range_in_window(
            scan, self.right_deg, self.window_half_width_deg)
        front_side = self.get_min_range_in_window(
            scan, self.front_right_deg, self.window_half_width_deg)

        # Compute dt for derivative term
        now = time.time()
        if self.last_time is None:
            dt = 0.1
        else:
            dt = max(1e-3, now - self.last_time)
        self.last_time = now

        cmd = Twist()

        if front < self.safety_distance:
            cmd.linear.x = 0.0
            cmd.angular.z = (
                +self.max_angular_speed if self.follow_side == "right" else -self.max_angular_speed
            )
            self.cmd_pub.publish(cmd)
            return

        #  PD wall following
        error = self.wall_distance - side
        derivative = (error - self.last_error) / dt
        self.last_error = error

        angular_z = (self.kp * error) + (self.kd * derivative)

        # Small corner help:
        if front_side < self.wall_distance:
            angular_z += 0.3 if self.follow_side == "right" else -0.3

        angular_z = clamp(angular_z, -self.max_angular_speed,
                          self.max_angular_speed)

        cmd.linear.x = self.linear_speed
        cmd.angular.z = angular_z

        self.cmd_pub.publish(cmd)

    def get_min_range_in_window(self, scan: LaserScan, center_deg: float, half_width_deg: float) -> float:
        """
        Return the minimum LiDAR distance within an angle window.
        Uses scan.angle_min and scan.angle_increment so it works for ANY lidar resolution.
        """
        # Make explicit floats to satisfy stricter type checkers
        center = math.radians(float(center_deg))
        half = math.radians(float(half_width_deg))

        start_angle = center - half
        end_angle = center + half

        # Guard: avoid divide-by-zero if scan is malformed
        if scan.angle_increment == 0.0:
            return scan.range_max

        start_i = int((start_angle - scan.angle_min) / scan.angle_increment)
        end_i = int((end_angle - scan.angle_min) / scan.angle_increment)

        n = len(scan.ranges)
        if n == 0:
            return scan.range_max

        start_i = max(0, min(start_i, n - 1))
        end_i = max(0, min(end_i, n - 1))

        if start_i > end_i:
            start_i, end_i = end_i, start_i

        min_val = scan.range_max
        for i in range(start_i, end_i + 1):
            r = sanitize_range(scan.ranges[i], scan.range_min, scan.range_max)
            if r < min_val:
                min_val = r

        return min_val


def main() -> None:
    rclpy.init()
    node = WallFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
