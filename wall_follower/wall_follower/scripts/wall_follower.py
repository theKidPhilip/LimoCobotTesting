#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy, DurabilityPolicy, LivelinessPolicy
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

import math


# =============================
# USER SETTINGS
# =============================

side_choice = "none"   # "left" or "right" or "none"
algo_choice = "min"    # "min" or "avg"


# =============================
# WALL FOLLOWER NODE
# =============================

class WallFollower(Node):

    def __init__(self):
        super().__init__('wall_follower_node')
        self.get_logger().info("Wall Follower Initializing...")

        # =============================
        # SPEED PARAMETERS (SAFE FOR REAL ROBOT)
        # =============================
        self.lin_vel_slow = 0.10
        self.lin_vel_fast = 0.15
        self.ang_vel_slow = 0.10
        self.ang_vel_fast = 0.40

        self.robot_radius = 0.10
        self.side_threshold_min = self.robot_radius + 0.05
        self.side_threshold_max = self.robot_radius + 0.10
        self.front_threshold = self.robot_radius + 0.40

        self.wall_found = False
        self.side_chosen = "none"

        self.twist_cmd = Twist()

        # =============================
        # Publisher
        # =============================
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # =============================
        # Callback Group
        # =============================
        self.callback_group = ReentrantCallbackGroup()

        # =============================
        # Laser Subscriber
        # =============================
        qos = QoSProfile(
            depth=10,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC
        )

        self.scan_ready = False
        self.scan_sub = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            qos,
            callback_group=self.callback_group
        )

        # =============================
        # Odometry Subscriber
        # =============================
        self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            qos,
            callback_group=self.callback_group
        )

        # =============================
        # Control Timer (10 Hz)
        # =============================
        self.create_timer(
            0.1,
            self.control_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info("Wall Follower Started.")

    # =====================================================
    # SCAN CALLBACK
    # =====================================================

    def scan_callback(self, msg: LaserScan):

        ranges = msg.ranges
        total = len(ranges)

        if total == 0:
            return

        front = total // 2
        right = front - int(math.radians(90) / msg.angle_increment)
        left  = front + int(math.radians(90) / msg.angle_increment)

        window = int(math.radians(15) / msg.angle_increment)

        self.front_range = self.get_min_range(ranges, front - window, front + window)
        self.right_range = self.get_min_range(ranges, right - window, right + window)
        self.left_range  = self.get_min_range(ranges, left - window, left + window)

        self.scan_ready = True

    # =====================================================
    # HELPER: GET MIN VALID RANGE
    # =====================================================

    def get_min_range(self, ranges, start, end):
        valid = [
            r for r in ranges[max(0, start):min(len(ranges), end)]
            if not math.isinf(r) and not math.isnan(r)
        ]
        if len(valid) == 0:
            return 10.0
        return min(valid)

    # =====================================================
    # ODOM CALLBACK (optional logging only)
    # =====================================================

    def odom_callback(self, msg):
        pass

    # =====================================================
    # MAIN CONTROL LOOP
    # =====================================================

    def control_callback(self):

        # Safety: if no scan yet → STOP
        if not self.scan_ready:
            self.stop_robot()
            return

        # =========================================
        # FIND WALL FIRST
        # =========================================
        if not self.wall_found:

            if self.front_range < self.front_threshold:
                self.wall_found = True
                self.stop_robot()

                if side_choice == "none":
                    if self.right_range < self.left_range:
                        self.side_chosen = "right"
                    else:
                        self.side_chosen = "left"
                else:
                    self.side_chosen = side_choice

                self.get_logger().info(f"Wall Found. Following {self.side_chosen} side.")
                return

            else:
                self.twist_cmd.linear.x = self.lin_vel_slow
                self.twist_cmd.angular.z = 0.0
                self.publish_cmd()
                return

        # =========================================
        # WALL FOLLOWING BEHAVIOR
        # =========================================

        # Obstacle in front → turn away
        if self.front_range < self.front_threshold:

            self.twist_cmd.linear.x = 0.05

            if self.side_chosen == "right":
                self.twist_cmd.angular.z = self.ang_vel_fast
            else:
                self.twist_cmd.angular.z = -self.ang_vel_fast

            self.publish_cmd()
            return

        # Follow selected side
        self.twist_cmd.linear.x = self.lin_vel_fast

        if self.side_chosen == "right":

            if self.right_range < self.side_threshold_min:
                self.twist_cmd.angular.z = self.ang_vel_slow
            elif self.right_range > self.side_threshold_max:
                self.twist_cmd.angular.z = -self.ang_vel_slow
            else:
                self.twist_cmd.angular.z = 0.0

        else:  # left side

            if self.left_range < self.side_threshold_min:
                self.twist_cmd.angular.z = -self.ang_vel_slow
            elif self.left_range > self.side_threshold_max:
                self.twist_cmd.angular.z = self.ang_vel_slow
            else:
                self.twist_cmd.angular.z = 0.0

        self.publish_cmd()

    # =====================================================
    # SAFETY STOP
    # =====================================================

    def stop_robot(self):
        self.twist_cmd.linear.x = 0.0
        self.twist_cmd.angular.z = 0.0
        self.publish_cmd()

    def publish_cmd(self):
        self.cmd_pub.publish(self.twist_cmd)


# =========================================================
# MAIN
# =========================================================

def main(args=None):
    rclpy.init(args=args)

    node = WallFollower()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info("Stopping robot...")
        node.stop_robot()
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()