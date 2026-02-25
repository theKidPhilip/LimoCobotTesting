#!/usr/bin/env python3
"""
wall_follower_node.py

Simple, robust wall follower for LIMO:
- Uses LaserScan (/scan)
- Publishes Twist (/cmd_vel)
- Follows the right wall by default
- Avoids obstacles in front

No keyboard input. Runs immediately.

Tune:
- desired_dist
- kp
- forward_speed
- max_ang
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


def _finite_min(values, default=10.0):
    m = default
    for v in values:
        if v is None:
            continue
        if math.isfinite(v) and v > 0.0:
            m = min(m, v)
    return m


class WallFollower(Node):
    def __init__(self):
        super().__init__("wall_follower_node")

        # ===== Parameters (you can ros2 param set these too) =====
        self.declare_parameter("follow_side", "right")   # "right" or "left"
        self.declare_parameter("desired_dist", 0.35)     # meters
        self.declare_parameter("kp", 1.2)
        self.declare_parameter("forward_speed", 0.18)    # m/s
        self.declare_parameter("slow_speed", 0.10)       # m/s
        self.declare_parameter("max_ang", 0.9)           # rad/s
        self.declare_parameter("front_stop", 0.40)       # m
        self.declare_parameter("front_turn", 0.60)       # m
        self.declare_parameter("sector_deg", 15)         # degrees each side

        self.follow_side = self.get_parameter("follow_side").value
        self.desired_dist = float(self.get_parameter("desired_dist").value)
        self.kp = float(self.get_parameter("kp").value)
        self.forward_speed = float(self.get_parameter("forward_speed").value)
        self.slow_speed = float(self.get_parameter("slow_speed").value)
        self.max_ang = float(self.get_parameter("max_ang").value)
        self.front_stop = float(self.get_parameter("front_stop").value)
        self.front_turn = float(self.get_parameter("front_turn").value)
        self.sector_deg = int(self.get_parameter("sector_deg").value)

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.scan_sub = self.create_subscription(LaserScan, "/scan", self.scan_cb, 10)

        self.last_scan = None
        self.timer = self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info("Wall follower running (auto).")
        self.get_logger().info(f"Follow side: {self.follow_side}, desired_dist: {self.desired_dist}m")

    def scan_cb(self, msg: LaserScan):
        self.last_scan = msg

    def get_sector_min(self, scan: LaserScan, center_deg: float, half_width_deg: float) -> float:
        # Convert degrees to index window around center
        # scan angles are in radians
        center = math.radians(center_deg)
        half = math.radians(half_width_deg)

        angle_min = scan.angle_min
        angle_inc = scan.angle_increment
        n = len(scan.ranges)

        def idx_from_angle(a):
            i = int((a - angle_min) / angle_inc)
            return max(0, min(n - 1, i))

        i0 = idx_from_angle(center - half)
        i1 = idx_from_angle(center + half)
        if i1 < i0:
            i0, i1 = i1, i0

        return _finite_min(scan.ranges[i0:i1 + 1], default=scan.range_max)

    def control_loop(self):
        if self.last_scan is None:
            return

        scan = self.last_scan
        half = float(self.sector_deg)

        # Front is 0 deg
        front = self.get_sector_min(scan, 0.0, half)

        # Right is -90 deg, Left is +90 deg (ROS standard)
        right = self.get_sector_min(scan, -90.0, half)
        left = self.get_sector_min(scan, 90.0, half)

        # Choose wall distance measurement based on follow_side
        if self.follow_side.lower() == "left":
            wall_dist = left
            sign = -1.0  # steering direction flips
        else:
            wall_dist = right
            sign = +1.0

        # Error: positive means too far from wall (need to steer toward wall)
        error = self.desired_dist - wall_dist

        twist = Twist()

        # Obstacle handling
        if front < self.front_stop:
            twist.linear.x = 0.0
            # Turn away from obstacle: if following right wall, turn left (+z)
            twist.angular.z = sign * (+self.max_ang)
        elif front < self.front_turn:
            twist.linear.x = self.slow_speed
            twist.angular.z = sign * (+0.6 * self.max_ang)
        else:
            twist.linear.x = self.forward_speed
            twist.angular.z = sign * (self.kp * error)

        # Clamp angular
        twist.angular.z = max(-self.max_ang, min(self.max_ang, twist.angular.z))

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # stop robot on exit
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()