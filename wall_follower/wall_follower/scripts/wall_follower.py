#!/usr/bin/env python3
"""
Wall follower node for REAL LIMO robot.

IMPORTANT SAFETY:
- This node starts moving immediately once it is launched.
- Lab requirement ("robot must NOT move until 'S' is pressed") is enforced
  by the external gate script: arm_then_run_wall_follower.

Topics:
- Subscribes: /scan  (sensor_msgs/LaserScan)
- Publishes:  /cmd_vel (geometry_msgs/Twist)

Behavior:
1) Move forward slowly until a wall is detected in front.
2) Stop, decide whether wall is on left/right (or use forced SIDE_CHOICE).
3) Follow chosen wall while avoiding obstacles in front.
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    HistoryPolicy,
    ReliabilityPolicy,
    DurabilityPolicy,
    LivelinessPolicy,
)
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


# ==============================
# USER SETTINGS (change here)
# ==============================

SIDE_CHOICE = "none"   # "left" or "right" or "none" (auto-pick)
ALGO_CHOICE = "min"    # "min" or "avg"


class WallFollower(Node):
    def __init__(self):
        super().__init__("wall_follower_node")
        self.get_logger().info("WallFollower: starting (armed by external 'S' gate).")

        # -------------------------
        # Thresholds / geometry
        # -------------------------
        self.robot_radius = 0.10
        self.side_threshold_min = self.robot_radius + 0.05
        self.side_threshold_max = self.robot_radius + 0.10
        self.front_threshold = self.robot_radius + 0.40

        # -------------------------
        # Safe speeds for real robot
        # -------------------------
        self.lin_vel_zero = 0.0
        self.lin_vel_slow = 0.10
        self.lin_vel_fast = 0.15   # keep <= 0.15
        self.ang_vel_zero = 0.0
        self.ang_vel_slow = 0.10
        self.ang_vel_fast = 0.40   # keep <= 0.45

        # -------------------------
        # State
        # -------------------------
        self.wall_found = False
        self.side_chosen = "none"
        self.scan_ready = False

        # Last scan ranges (meters)
        self.scan_left_range = 10.0
        self.scan_front_range = 10.0
        self.scan_right_range = 10.0

        # cmd vel message
        self.twist_cmd = Twist()

        # -------------------------
        # ROS interfaces
        # -------------------------
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.cb_group = ReentrantCallbackGroup()
        qos = QoSProfile(
            depth=10,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC,
        )

        self.create_subscription(
            LaserScan, "/scan", self.scan_callback, qos, callback_group=self.cb_group
        )

        # Control at 10 Hz (0.1s). Faster response than 0.5s timer.
        self.create_timer(0.1, self.control_callback, callback_group=self.cb_group)

        self.get_logger().info("WallFollower: ready.")

    # -------------------------
    # Helper functions
    # -------------------------
    @staticmethod
    def _valid_vals(segment):
        """Return list of valid ranges (finite, non-nan)."""
        return [r for r in segment if (not math.isinf(r) and not math.isnan(r))]

    def _segment_stat(self, segment):
        """Compute min or avg depending on ALGO_CHOICE."""
        vals = self._valid_vals(segment)
        if not vals:
            return 10.0
        if ALGO_CHOICE == "avg":
            return sum(vals) / len(vals)
        return min(vals)

    def stop_robot(self):
        """Immediately stop robot."""
        self.twist_cmd.linear.x = 0.0
        self.twist_cmd.angular.z = 0.0
        self.cmd_pub.publish(self.twist_cmd)

    def publish_cmd(self):
        """Clamp speeds and publish."""
        # linear clamp
        if self.twist_cmd.linear.x > 0.15:
            self.twist_cmd.linear.x = 0.15
        if self.twist_cmd.linear.x < -0.15:
            self.twist_cmd.linear.x = -0.15

        # angular clamp
        if self.twist_cmd.angular.z > 0.45:
            self.twist_cmd.angular.z = 0.45
        if self.twist_cmd.angular.z < -0.45:
            self.twist_cmd.angular.z = -0.45

        self.cmd_pub.publish(self.twist_cmd)

    # -------------------------
    # Scan callback
    # -------------------------
    def scan_callback(self, msg: LaserScan):
        total = len(msg.ranges)
        if total == 0:
            return

        # Index for 0 degrees (front)
        front_i = total // 2

        # 90 degrees in index steps (based on angle_increment in radians)
        ninety = int((math.pi / 2.0) / msg.angle_increment)
        right_i = front_i - ninety
        left_i = front_i + ninety

        # +/- 15 degrees window
        window = int(math.radians(15.0) / msg.angle_increment)

        def seg(center):
            a = max(0, center - window)
            b = min(total, center + window)
            return msg.ranges[a:b]

        self.scan_front_range = self._segment_stat(seg(front_i))
        self.scan_right_range = self._segment_stat(seg(right_i))
        self.scan_left_range = self._segment_stat(seg(left_i))

        self.scan_ready = True

    # -------------------------
    # Control loop
    # -------------------------
    def control_callback(self):
        # If no scan yet: stop for safety
        if not self.scan_ready:
            self.stop_robot()
            return

        # 1) Find wall first
        if not self.wall_found:
            if self.scan_front_range < self.front_threshold:
                self.wall_found = True
                self.stop_robot()

                # Choose which side wall is on
                if SIDE_CHOICE in ("left", "right"):
                    self.side_chosen = SIDE_CHOICE
                else:
                    # pick side with closer distance
                    self.side_chosen = "right" if (self.scan_right_range < self.scan_left_range) else "left"

                self.get_logger().info(f"Wall found. Following: {self.side_chosen}")
                return

            # no wall in front yet → creep forward
            self.twist_cmd.linear.x = self.lin_vel_slow
            self.twist_cmd.angular.z = 0.0
            self.publish_cmd()
            return

        # 2) Wall following
        # obstacle ahead → turn away from wall side
        if self.scan_front_range < self.front_threshold:
            self.twist_cmd.linear.x = 0.05
            if self.side_chosen == "right":
                # wall on right → turn left
                self.twist_cmd.angular.z = +self.ang_vel_fast
            else:
                # wall on left → turn right
                self.twist_cmd.angular.z = -self.ang_vel_fast
            self.publish_cmd()
            return

        # otherwise, follow at fast speed and adjust distance to wall
        self.twist_cmd.linear.x = self.lin_vel_fast

        if self.side_chosen == "right":
            # Too close → turn left
            if self.scan_right_range < self.side_threshold_min:
                self.twist_cmd.angular.z = +self.ang_vel_slow
            # Too far → turn right
            elif self.scan_right_range > self.side_threshold_max:
                self.twist_cmd.angular.z = -self.ang_vel_slow
            else:
                self.twist_cmd.angular.z = 0.0
        else:
            # Too close → turn right
            if self.scan_left_range < self.side_threshold_min:
                self.twist_cmd.angular.z = -self.ang_vel_slow
            # Too far → turn left
            elif self.scan_left_range > self.side_threshold_max:
                self.twist_cmd.angular.z = +self.ang_vel_slow
            else:
                self.twist_cmd.angular.z = 0.0

        self.publish_cmd()


def main(args=None):
    rclpy.init(args=args)

    node = WallFollower()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info("WallFollower: stopping robot...")
        node.stop_robot()
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()