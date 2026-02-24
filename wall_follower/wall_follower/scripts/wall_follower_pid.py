#!/usr/bin/env python3

# ============================================================
# File: wall_follower_pid.py
# Project: AshBot Wall Follower (PID Control)
# Brief: Wall follower node using full Proportional-Integral-
#        Derivative (PID) control for precise wall tracking.
#
# PID Control Law (angular velocity):
#   error      = desired_wall_dist - actual_wall_dist
#   integral  += error * dt                 (accumulated over time)
#   derivative = (error - prev_error) / dt
#   angular_z  = Kp * error + Ki * integral + Kd * derivative
#
# Positive error  → robot too far from wall  → steer toward wall
# Negative error  → robot too close to wall  → steer away
#
# The integral term corrects steady-state bias (e.g. the robot
# consistently running 2 cm too far from the wall).  Anti-windup
# clamps the integral so it cannot grow unbounded on long straight
# sections or when the robot is stuck.
# ============================================================

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import (HistoryPolicy, ReliabilityPolicy,
                       DurabilityPolicy, LivelinessPolicy)
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

import math
import sys
import select
import tty
import termios
import threading
import time

# ─────────────────────────────────────────────
# Global Settings
# ─────────────────────────────────────────────

# Side bias: "left" | "right" | "none"
side_choice = "none"

# Scan aggregation: "min" | "avg"
algo_choice = "min"

# ─── PID Gains ───────────────────────────────
# Kp – proportional: main correction force
# Ki – integral:     removes steady-state offset
# Kd – derivative:   damps oscillation
Kp = 1.800
Ki = 0.050
Kd = 0.900

# Anti-windup: maximum absolute value for the integral accumulator
INTEGRAL_MAX = 0.500
# ─────────────────────────────────────────────


class WallFollowerPID(Node):
    """Wall follower node using full PID control."""

    # ── robot geometry ──────────────────────────────────────────
    robot_radius = 0.10
    side_threshold_min = robot_radius + 0.05
    side_threshold_max = robot_radius + 0.10
    desired_wall_dist = robot_radius + 0.075   # midpoint setpoint
    front_threshold = robot_radius + 0.40

    # ── velocity limits ──────────────────────────────────────────
    lin_vel_zero = 0.000
    lin_vel_slow = 0.100
    lin_vel_fast = 0.200
    ang_vel_zero = 0.000
    ang_vel_max = 0.500

    # ── math helpers ─────────────────────────────────────────────
    pi = 3.141592654
    pi_inv = 0.318309886

    # ── scan setup ───────────────────────────────────────────────
    scan_sides_angle_range = 15
    scan_front_angle_range = 15

    # ── startup / state ──────────────────────────────────────────
    ignore_iterations = 5
    iterations_count = 0
    wall_found = False
    side_chosen = "none"

    # ── scan data ────────────────────────────────────────────────
    scan_info_done = False
    scan_angle_min = 0.0
    scan_angle_max = 0.0
    scan_angle_inc = 0.0
    scan_range_min = 0.0
    scan_range_max = 0.0
    scan_right_range = 0.0
    scan_front_range = 0.0
    scan_left_range = 0.0
    scan_angle_range = 0
    scan_ranges_size = 0
    scan_right_index = 0
    scan_front_index = 0
    scan_left_index = 0
    scan_right_range_from_index = 0
    scan_right_range_to_index = 0
    scan_front_range_from_index = 0
    scan_front_range_to_index = 0
    scan_left_range_from_index = 0
    scan_left_range_to_index = 0

    # ── odometry data ────────────────────────────────────────────
    odom_info_done = False
    odom_initial_x = 0.0
    odom_initial_y = 0.0
    odom_initial_yaw = 0.0
    odom_curr_x = 0.0
    odom_curr_y = 0.0
    odom_curr_yaw = 0.0
    odom_prev_x = 0.0
    odom_prev_y = 0.0
    odom_prev_yaw = 0.0
    odom_distance = 0.0

    # ── PID state ────────────────────────────────────────────────
    pid_prev_error = 0.0
    pid_integral = 0.0           # accumulated integral term
    pid_prev_time = None

    # ── velocity command ─────────────────────────────────────────
    twist_cmd = Twist()

    # ─────────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__('wall_follower_pid')
        self.get_logger().info("Initialising Wall Follower (PID Control) ...")

        self.cmd_vel_pub = self.create_publisher(
            msg_type=Twist, topic="/cmd_vel", qos_profile=10)
        self.get_logger().info("Initialised /cmd_vel publisher")

        self.callback_group = ReentrantCallbackGroup()

        scan_qos = QoSProfile(
            depth=10,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC)
        self.scan_sub = self.create_subscription(
            msg_type=LaserScan, topic="/scan",
            callback=self.scan_callback,
            qos_profile=scan_qos,
            callback_group=self.callback_group)
        self.get_logger().info("Initialised /scan subscriber")

        odom_qos = QoSProfile(
            depth=10,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC)
        self.odom_sub = self.create_subscription(
            msg_type=Odometry, topic="/odom",
            callback=self.odom_callback,
            qos_profile=odom_qos,
            callback_group=self.callback_group)
        self.get_logger().info("Initialised /odom subscriber")

        # 10 Hz control loop
        self.control_timer = self.create_timer(
            timer_period_sec=0.100,
            callback=self.control_callback,
            callback_group=self.callback_group)
        self.get_logger().info("Initialised control timer (10 Hz)")

        self.enabled = False
        self.key_thread = threading.Thread(
            target=self.keyboard_listener, daemon=True)
        self.key_thread.start()
        self.get_logger().info("Press 's' to toggle wall following, 'q' to quit.")
        self.get_logger().info("Wall Follower PID Initialised !")
        self.get_logger().info(
            "PID Gains: Kp=%.3f  Ki=%.3f  Kd=%.3f  I_max=%.3f" %
            (Kp, Ki, Kd, INTEGRAL_MAX))

    # ─── keyboard ────────────────────────────────────────────────
    def keyboard_listener(self):
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            while rclpy.ok():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key == 's':
                        self.enabled = not self.enabled
                        state = 'ENABLED' if self.enabled else 'DISABLED'
                        self.get_logger().info(f"Wall following {state}")
                        if not self.enabled:
                            self.twist_cmd.linear.x = 0.0
                            self.twist_cmd.angular.z = 0.0
                            self.cmd_vel_pub.publish(self.twist_cmd)
                            # Reset all PID state to avoid stale terms
                            self._reset_pid()
                    elif key == 'q':
                        self.get_logger().info("Quit requested.")
                        rclpy.shutdown()
                        break
        except Exception as exc:
            self.get_logger().error(f"Keyboard thread error: {exc}")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    # ─── scan callback ───────────────────────────────────────────
    def scan_callback(self, scan_msg):
        if self.scan_info_done:
            self._process_scan_ranges(scan_msg)
        else:
            self._initialise_scan_info(scan_msg)

    def _process_scan_ranges(self, scan_msg):
        if algo_choice == "avg":
            r_sum, f_sum, l_sum = 0.0, 0.0, 0.0
            r_cnt, f_cnt, l_cnt = 0,   0,   0
            for i, r in enumerate(scan_msg.ranges):
                if math.isinf(r):
                    continue
                if self.scan_right_range_from_index <= i <= self.scan_right_range_to_index:
                    r_sum += r
                    r_cnt += 1
                if self.scan_front_range_from_index <= i <= self.scan_front_range_to_index:
                    f_sum += r
                    f_cnt += 1
                if self.scan_left_range_from_index <= i <= self.scan_left_range_to_index:
                    l_sum += r
                    l_cnt += 1
            self.scan_right_range = (
                r_sum / r_cnt) if r_cnt else self.scan_range_min
            self.scan_front_range = (
                f_sum / f_cnt) if f_cnt else self.scan_range_min
            self.scan_left_range = (
                l_sum / l_cnt) if l_cnt else self.scan_range_min
        else:  # min
            r_min = f_min = l_min = self.scan_range_max
            for i, r in enumerate(scan_msg.ranges):
                if math.isinf(r):
                    continue
                if self.scan_right_range_from_index <= i <= self.scan_right_range_to_index:
                    r_min = min(r_min, r)
                if self.scan_front_range_from_index <= i <= self.scan_front_range_to_index:
                    f_min = min(f_min, r)
                if self.scan_left_range_from_index <= i <= self.scan_left_range_to_index:
                    l_min = min(l_min, r)
            self.scan_right_range = r_min if r_min > 0.0 else self.scan_range_min
            self.scan_front_range = f_min if f_min > 0.0 else self.scan_range_min
            self.scan_left_range = l_min if l_min > 0.0 else self.scan_range_min

    def _initialise_scan_info(self, scan_msg):
        self.scan_angle_min = scan_msg.angle_min
        self.scan_angle_max = scan_msg.angle_max
        self.scan_range_min = scan_msg.range_min
        self.scan_range_max = scan_msg.range_max
        self.scan_ranges_size = len(scan_msg.ranges)
        self.scan_angle_range = int(
            (abs(self.scan_angle_min) + abs(self.scan_angle_max)) * (180.0 / self.pi))
        self.scan_angle_inc = self.scan_angle_range / self.scan_ranges_size

        self.scan_front_index = self.scan_ranges_size // 2
        self.scan_right_index = (self.scan_front_index -
                                 int(90.0 / self.scan_angle_inc) - 1)
        self.scan_left_index = (self.scan_front_index +
                                int(90.0 / self.scan_angle_inc) + 1)

        self.scan_front_range_from_index = (self.scan_front_index -
                                            int(self.scan_front_angle_range / self.scan_angle_inc))
        self.scan_front_range_to_index = (self.scan_front_index +
                                          int(self.scan_front_angle_range / self.scan_angle_inc))

        if self.scan_angle_range > 180:
            half = int(self.scan_sides_angle_range / self.scan_angle_inc)
            self.scan_right_range_from_index = self.scan_right_index - half
            self.scan_right_range_to_index = self.scan_right_index + half
            self.scan_left_range_from_index = self.scan_left_index - half
            self.scan_left_range_to_index = self.scan_left_index + half
        else:
            half = int(self.scan_sides_angle_range / self.scan_angle_inc)
            self.scan_right_range_from_index = self.scan_right_index
            self.scan_right_range_to_index = self.scan_right_index + half
            self.scan_left_range_from_index = self.scan_left_index - half
            self.scan_left_range_to_index = self.scan_left_index

        self.scan_info_done = True
        self.get_logger().info("Scan info initialised.")

    # ─── odom callback ───────────────────────────────────────────
    def odom_callback(self, odom_msg):
        pos = odom_msg.pose.pose.position
        ori = odom_msg.pose.pose.orientation
        angles = self.euler_from_quaternion(ori.x, ori.y, ori.z, ori.w)

        if self.odom_info_done:
            self.odom_curr_x = pos.x
            self.odom_curr_y = pos.y
            self.odom_curr_yaw = angles["yaw_deg"]
            self.odom_distance += self.calculate_distance(
                self.odom_prev_x, self.odom_prev_y, pos.x, pos.y)
            self.odom_prev_x = self.odom_curr_x
            self.odom_prev_y = self.odom_curr_y
            self.odom_prev_yaw = self.odom_curr_yaw
        else:
            self.odom_initial_x = pos.x
            self.odom_initial_y = pos.y
            self.odom_initial_yaw = angles["yaw_deg"]
            self.odom_prev_x = pos.x
            self.odom_prev_y = pos.y
            self.odom_prev_yaw = angles["yaw_deg"]
            self.odom_info_done = True
            self.get_logger().info(
                "Odom info initialised: x=%+.3f y=%+.3f yaw=%+.3f" %
                (pos.x, pos.y, angles["yaw_deg"]))

    # ─── control callback ────────────────────────────────────────
    def control_callback(self):
        if self.iterations_count < self.ignore_iterations:
            self.iterations_count += 1
            self._stop_robot()
            self._publish()
            return

        if not self.enabled:
            self._stop_robot()
            self._publish()
            return

        if not self.wall_found:
            self._search_for_wall()
        else:
            self._follow_wall_pid()

        self._publish()
        self._print_info()

    # ── phase 1: drive toward nearest wall ───────────────────────
    def _search_for_wall(self):
        if self.scan_front_range < self.front_threshold:
            self.wall_found = True
            self.get_logger().info("Wall found!")
            self._stop_robot()

            if side_choice not in ("right", "left"):
                self.side_chosen = "right" if self.scan_right_range <= self.scan_left_range else "left"
            else:
                self.side_chosen = side_choice
            self.get_logger().info(f"Side chosen: {self.side_chosen}")

            # Initialise PID state cleanly
            self._reset_pid()
        else:
            self.twist_cmd.linear.x = self.lin_vel_slow
            self.twist_cmd.angular.z = self.ang_vel_zero

    # ── phase 2: PID wall following ──────────────────────────────
    def _follow_wall_pid(self):
        now = time.monotonic()
        dt = (now - self.pid_prev_time) if self.pid_prev_time is not None else 0.1
        dt = max(dt, 1e-4)
        self.pid_prev_time = now

        # ── relevant side range ───────────────────────────────────
        side_range = (self.scan_right_range
                      if self.side_chosen == "right"
                      else self.scan_left_range)

        # ── PID terms ─────────────────────────────────────────────
        error = self.desired_wall_dist - side_range

        # Integral with anti-windup clamping
        self.pid_integral += error * dt
        self.pid_integral = max(
            min(self.pid_integral, INTEGRAL_MAX), -INTEGRAL_MAX)

        derivative = (error - self.pid_prev_error) / dt
        self.pid_prev_error = error

        pid_output = (Kp * error) + (Ki * self.pid_integral) + \
            (Kd * derivative)

        # ── sign convention ───────────────────────────────────────
        if self.side_chosen == "right":
            angular_correction = -pid_output
        else:
            angular_correction = pid_output

        # ── obstacle avoidance overrides PID ─────────────────────
        if self.scan_front_range < self.front_threshold:
            # Hard escape turn; reset integral so it doesn't fight recovery
            self.pid_integral = 0.0
            self.twist_cmd.linear.x = self.lin_vel_slow
            if self.side_chosen == "right":
                self.twist_cmd.angular.z = self.ang_vel_max
            else:
                self.twist_cmd.angular.z = -self.ang_vel_max
        else:
            self.twist_cmd.linear.x = self.lin_vel_fast
            self.twist_cmd.angular.z = angular_correction

        self.get_logger().info(
            "PID | err=%+.4f  intg=%+.4f  deriv=%+.4f  out=%+.4f  ang=%+.4f" %
            (error, self.pid_integral, derivative, pid_output,
             self.twist_cmd.angular.z))

    # ─── helpers ─────────────────────────────────────────────────
    def _reset_pid(self):
        """Reset all PID state variables."""
        self.pid_prev_error = 0.0
        self.pid_integral = 0.0
        self.pid_prev_time = time.monotonic()

    def _stop_robot(self):
        self.twist_cmd.linear.x = self.lin_vel_zero
        self.twist_cmd.angular.z = self.ang_vel_zero

    def _publish(self):
        self.twist_cmd.linear.x = max(
            min(self.twist_cmd.linear.x,  self.lin_vel_fast), -self.lin_vel_fast)
        self.twist_cmd.angular.z = max(
            min(self.twist_cmd.angular.z, self.ang_vel_max), -self.ang_vel_max)
        self.cmd_vel_pub.publish(self.twist_cmd)

    def _print_info(self):
        self.get_logger().info(
            "Scan  L:%.3f  F:%.3f  R:%.3f" %
            (self.scan_left_range, self.scan_front_range, self.scan_right_range))
        self.get_logger().info(
            "Odom  x:%+.3f  y:%+.3f  yaw:%+.3f  dist:%.3f" %
            (self.odom_curr_x, self.odom_curr_y,
             self.odom_curr_yaw, self.odom_distance))
        self.get_logger().info(
            "Vel   lin:%+.3f  ang:%+.3f" %
            (self.twist_cmd.linear.x, self.twist_cmd.angular.z))
        self.get_logger().info("~~~~~~~~~~")

    def calculate_distance(self, px, py, cx, cy):
        return math.hypot(cx - px, cy - py)

    def euler_from_quaternion(self, qx, qy, qz, qw):
        sinr = 2 * (qw * qx + qy * qz)
        cosr = 1 - 2 * (qx * qx + qy * qy)
        roll_rad = math.atan2(sinr, cosr)

        sinp = 2 * (qw * qy - qz * qx)
        pitch_rad = math.asin(sinp)

        siny = 2 * (qw * qz + qx * qy)
        cosy = 1 - 2 * (qy * qy + qz * qz)
        yaw_rad = math.atan2(siny, cosy)

        return {
            "roll_rad":  roll_rad,  "roll_deg":  roll_rad * 180 * self.pi_inv,
            "pitch_rad": pitch_rad, "pitch_deg": pitch_rad * 180 * self.pi_inv,
            "yaw_rad":   yaw_rad,   "yaw_deg":   yaw_rad * 180 * self.pi_inv,
        }


# ─────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = WallFollowerPID()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info("Stopping robot ...")
        node._stop_robot()
        node._publish()
        node.get_logger().info("Wall Follower PID stopped.")
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
