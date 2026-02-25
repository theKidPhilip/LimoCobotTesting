# !/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import HistoryPolicy, ReliabilityPolicy, DurabilityPolicy, LivelinessPolicy
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

import math
import sys
import select
import tty
import termios
import threading

# ---------------- GLOBAL SETTINGS ----------------

side_choice = "none"   # "left" or "right" or "none"

# ---------------- WALL FOLLOWER ----------------

class WallFollower(Node):

    def __init__(self):
        super().__init__('ackermann_wall_follower')

        self.get_logger().info("Initializing Ackermann Wall Follower...")

        # ---------------- Robot Parameters ----------------

        self.robot_radius = 0.10

        # IMPORTANT: larger detection distance for car-like robot
        self.front_threshold = 0.75
        self.side_threshold_min = 0.18
        self.side_threshold_max = 0.28

        # Speeds
        self.lin_zero = 0.0
        self.lin_slow = 0.12
        self.lin_fast = 0.18
        self.lin_reverse = -0.08

        self.ang_zero = 0.0
        self.ang_turn = 0.6
        self.ang_adjust = 0.25

        # State machine
        self.wall_found = False
        self.side_chosen = "none"
        self.escape_mode = False
        self.escape_counter = 0

        # Scan variables
        self.scan_ready = False
        self.scan_right = float('inf')
        self.scan_left = float('inf')
        self.scan_front = float('inf')

        self.twist_cmd = Twist()

        # Publisher
        self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        qos = QoSProfile(
            depth=10,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC
        )

        self.callback_group = ReentrantCallbackGroup()

        self.scan_sub = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            qos,
            callback_group=self.callback_group
        )

        self.control_timer = self.create_timer(
            0.1,
            self.control_callback,
            callback_group=self.callback_group
        )

        # Keyboard
        self.enabled = False
        self.key_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.key_thread.start()

        self.get_logger().info("Press 's' to toggle, 'q' to quit.")

    # -------------------------------------------------
    # ---------------- KEYBOARD -----------------------
    # -------------------------------------------------

    def keyboard_listener(self):
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        try:
            while rclpy.ok():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)

                    if key == 's':
                        self.enabled = not self.enabled
                        self.get_logger().info(
                            f"Wall Following {'ENABLED' if self.enabled else 'DISABLED'}"
                        )
                        if not self.enabled:
                            self.stop_robot()

                    elif key == 'q':
                        rclpy.shutdown()
                        break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    # -------------------------------------------------
    # ---------------- SCAN CALLBACK ------------------
    # -------------------------------------------------

    def scan_callback(self, msg):

        ranges = msg.ranges
        size = len(ranges)
        center = size // 2

        right_index = center - 90
        left_index = center + 90

        if 0 <= center < size:
            self.scan_front = ranges[center]

        if 0 <= right_index < size:
            self.scan_right = ranges[right_index]

        if 0 <= left_index < size:
            self.scan_left = ranges[left_index]

        self.scan_ready = True

    # -------------------------------------------------
    # ---------------- CONTROL ------------------------
    # -------------------------------------------------

    def control_callback(self):

        if not self.enabled or not self.scan_ready:
            return

        # ---------------- ESCAPE MODE ----------------
        # Reverse first to create turning radius

        if self.escape_mode:

            if self.escape_counter < 5:
                # Reverse straight
                self.twist_cmd.linear.x = self.lin_reverse
                self.twist_cmd.angular.z = 0.0
                self.escape_counter += 1

            else:
                # Turn while moving forward
                self.twist_cmd.linear.x = self.lin_slow
                if self.side_chosen == "right":
                    self.twist_cmd.angular.z = self.ang_turn
                else:
                    self.twist_cmd.angular.z = -self.ang_turn

                # Exit escape if front is clear
                if self.scan_front > self.front_threshold:
                    self.escape_mode = False
                    self.escape_counter = 0

            self.publish()
            return

        # ---------------- FIND WALL ----------------

        if not self.wall_found:

            if self.scan_front < self.front_threshold:
                self.wall_found = True

                if side_choice == "none":
                    if self.scan_right < self.scan_left:
                        self.side_chosen = "right"
                    else:
                        self.side_chosen = "left"
                else:
                    self.side_chosen = side_choice

                self.get_logger().info(f"Following {self.side_chosen} wall")
            else:
                self.twist_cmd.linear.x = self.lin_slow
                self.twist_cmd.angular.z = 0.0
                self.publish()
                return

        # ---------------- FRONT OBSTACLE ----------------

        if self.scan_front < self.front_threshold:
            self.escape_mode = True
            self.escape_counter = 0
            return

        # ---------------- WALL FOLLOWING ----------------

        self.twist_cmd.linear.x = self.lin_fast

        if self.side_chosen == "right":

            if self.scan_right < self.side_threshold_min:
                self.twist_cmd.angular.z = self.ang_adjust

            elif self.scan_right > self.side_threshold_max:
                self.twist_cmd.angular.z = -self.ang_adjust

            else:
                self.twist_cmd.angular.z = 0.0

        elif self.side_chosen == "left":

            if self.scan_left < self.side_threshold_min:
                self.twist_cmd.angular.z = -self.ang_adjust

            elif self.scan_left > self.side_threshold_max:
                self.twist_cmd.angular.z = self.ang_adjust

            else:
                self.twist_cmd.angular.z = 0.0

        self.publish()

    # -------------------------------------------------
    # ---------------- UTILITIES ----------------------
    # -------------------------------------------------

    def publish(self):

        # Clamp linear
        if self.twist_cmd.linear.x > 0.2:
            self.twist_cmd.linear.x = 0.2
        if self.twist_cmd.linear.x < -0.1:
            self.twist_cmd.linear.x = -0.1

        # Clamp angular
        if self.twist_cmd.angular.z > 0.8:
            self.twist_cmd.angular.z = 0.8
        if self.twist_cmd.angular.z < -0.8:
            self.twist_cmd.angular.z = -0.8

        self.cmd_vel_pub.publish(self.twist_cmd)

    def stop_robot(self):
        self.twist_cmd.linear.x = 0.0
        self.twist_cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(self.twist_cmd)

# -------------------------------------------------

# ---------------- MAIN ---------------------------

# -------------------------------------------------

def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()

    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
