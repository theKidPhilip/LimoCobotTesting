#!/usr/bin/env python3

# ============================================================
# File: wall_follower_pd.py
# Project: AshBot Wall Follower (PD Control)
# Brief: Wall follower node using Proportional-Derivative (PD)
#        control for smooth, responsive wall tracking.
#
# PD Control Law (angular velocity):
#   error      = desired_wall_dist - actual_wall_dist
#   derivative = (error - prev_error) / dt
#   angular_z  = Kp * error + Kd * derivative
#
# Positive error  → robot too far from wall  → turn toward wall
# Negative error  → robot too close to wall  → turn away from wall
#
# Changes made vs old version:
#  1) Increased speeds (Gazebo looked slow)
#  2) Increased angular cap so it can steer properly at higher speed
#  3) Added "slow down on sharp turns" for stability at higher speed
#  4) Reduced logging rate (logs every 1 second instead of every 0.1s)
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

# Side bias: "left" | "right" | "none"  (none = auto-detect closest wall)
side_choice = "none"

# Scan aggregation algorithm: "min" | "avg"
# If you see jitter at higher speed, try "avg"
algo_choice = "min"

# ─── PD Gains ────────────────────────────────
# Kp: how hard to correct for wall distance error
# Kd: how hard to damp rapid changes in error (reduces oscillation)
Kp = 1.800
Kd = 0.900
# ─────────────────────────────────────────────


class WallFollowerPD(Node):
    """Wall follower node using Proportional-Derivative (PD) control."""

    # ── robot geometry ──────────────────────────────────────────
    robot_radius = 0.10          # metres
    side_threshold_min = robot_radius + 0.05   # 5 cm gap  (too close)
    side_threshold_max = robot_radius + 0.10   # 10 cm gap (too far)
    desired_wall_dist = robot_radius + 0.075  # midpoint of the corridor
    front_threshold = robot_radius + 0.40     # 40 cm – obstacle ahead

    # ── velocity limits (UPDATED: faster) ───────────────────────
    lin_vel_zero = 0.000
    lin_vel_slow = 0.200          # was 0.100
    lin_vel_fast = 0.450          # was 0.200
    ang_vel_zero = 0.000
    ang_vel_max = 1.200           # was 0.500

    # ── dynamic speed scaling (NEW) ─────────────────────────────
    # When turning hard, reduce forward speed so it doesn't crash / oscillate.
    turn_slowdown_gain = 0.60     # 0.0 = no slowdown, 0.6 is a good start

    # ── logging throttling (NEW) ────────────────────────────────
    # 10 Hz control loop -> print debug every 10 ticks = 1 second
    debug_every_ticks = 10

    # ── math helpers ─────────────────────────────────────────────
    pi = 3.141592654
    pi_inv = 0.318309886

    # ── scan setup ───────────────────────────────────────────────
    scan_sides_angle_range = 15     # degrees each side of the 90-deg beam
    scan_front_angle_range = 15     # degrees each side of the front beam

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

    # ── PD state ─────────────────────────────────────────────────
    pd_prev_error = 0.0           # previous error  (for derivative term)
    pd_prev_time = None           # timestamp of previous control call

    # ── velocity command ─────────────────────────────────────────
    twist_cmd = Twist()

    # ─────────────────────────────────────────────
    def __init__(self):
        super().__init__('wall_follower_pd')
        self.get_logger().info("Initialising Wall Follower (PD Control) ...")

        # (NEW) debug tick counter for throttling logs
        self.debug_tick = 0

        # cmd_vel publisher
        self.cmd_vel_pub = self.create_publisher(
            msg_type=Twist, topic="/cmd_vel", qos_profile=10)
        self.get_logger().info("Initialised /cmd_vel publisher")

        self.callback_group = ReentrantCallbackGroup()

        # LaserScan subscriber
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

        # Odometry subscriber
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

        # Control timer – 10 Hz
        self.control_timer = self.create_timer(
            timer_period_sec=0.100,
            callback=self.control_callback,
            callback_group=self.callback_group)
        self.get_logger().info("Initialised control timer (10 Hz)")

        # Keyboard toggle
        self.enabled = False
        self.key_thread = threading.Thread(
            target=self.keyboard_listener, daemon=True)
        self.key_thread.start()

        self.get_logger().info("Press 's' to toggle wall following, 'q' to quit.")
        self.get_logger().info(
            f"Speed caps: lin_fast={self.lin_vel_fast:.2f} m/s, "
            f"lin_slow={self.lin_vel_slow:.2f} m/s, ang_max={self.ang_vel_max:.2f} rad/s"
        )
        self.get_logger().info("Wall Follower PD Initialised !")

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
                            # reset PD state on disable so there is no
                            # stale derivative on next enable
                            self.pd_prev_error = 0.0
                            self.pd_prev_time = None
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
        """Update right / front / left range readings."""
        if algo_choice == "avg":
            r_sum, f_sum, l_sum = 0.0, 0.0, 0.0
            r_cnt, f_cnt, l_cnt = 0, 0, 0
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

            self.scan_right_range = (r_sum / r_cnt) if r_cnt else self.scan_range_min
            self.scan_front_range = (f_sum / f_cnt) if f_cnt else self.scan_range_min
            self.scan_left_range = (l_sum / l_cnt) if l_cnt else self.scan_range_min
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
        """Run once: compute all fixed scan indices."""
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

        half = int(self.scan_sides_angle_range / self.scan_angle_inc)
        if self.scan_angle_range > 180:
            self.scan_right_range_from_index = self.scan_right_index - half
            self.scan_right_range_to_index = self.scan_right_index + half
            self.scan_left_range_from_index = self.scan_left_index - half
            self.scan_left_range_to_index = self.scan_left_index + half
        else:
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
        # Honour startup ignore period regardless of enable state
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
            self._follow_wall_pd()

        self._publish()

        # (UPDATED) Print info only every 1 second to reduce lag
        self.debug_tick += 1
        if self.debug_tick % self.debug_every_ticks == 0:
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

            # seed PD state
            self.pd_prev_error = 0.0
            self.pd_prev_time = time.monotonic()
        else:
            self.twist_cmd.linear.x = self.lin_vel_slow
            self.twist_cmd.angular.z = self.ang_vel_zero

    # ── phase 2: PD wall following ───────────────────────────────
    def _follow_wall_pd(self):
        now = time.monotonic()
        dt = (now - self.pd_prev_time) if self.pd_prev_time is not None else 0.1
        dt = max(dt, 1e-4)  # guard against zero dt
        self.pd_prev_time = now

        # ── choose the relevant side range ───────────────────────
        side_range = self.scan_right_range if self.side_chosen == "right" else self.scan_left_range

        # ── compute PD terms ─────────────────────────────────────
        error = self.desired_wall_dist - side_range
        derivative = (error - self.pd_prev_error) / dt
        self.pd_prev_error = error

        # ── raw PD output ─────────────────────────────────────────
        pd_output = (Kp * error) + (Kd * derivative)

        # ── sign convention ───────────────────────────────────────
        angular_correction = -pd_output if self.side_chosen == "right" else pd_output

        # ── obstacle avoidance overrides PD ──────────────────────
        if self.scan_front_range < self.front_threshold:
            # Hard turn away from wall while barely moving
            self.twist_cmd.linear.x = self.lin_vel_slow
            self.twist_cmd.angular.z = self.ang_vel_max if self.side_chosen == "right" else -self.ang_vel_max
        else:
            # Normal PD tracking
            self.twist_cmd.angular.z = angular_correction

            # (NEW) Slow down on sharp turns for stability at higher speed
            turn_strength = abs(self.twist_cmd.angular.z) / self.ang_vel_max  # 0..1
            self.twist_cmd.linear.x = self.lin_vel_fast * (1.0 - self.turn_slowdown_gain * turn_strength)
            self.twist_cmd.linear.x = max(self.twist_cmd.linear.x, self.lin_vel_slow)

        # (UPDATED) PD debug log only every 1 second to reduce lag
        if self.debug_tick % self.debug_every_ticks == 0:
            self.get_logger().info(
                "PD | err=%+.4f  deriv=%+.4f  out=%+.4f  ang=%+.4f  lin=%+.4f" %
                (error, derivative, pd_output,
                 self.twist_cmd.angular.z, self.twist_cmd.linear.x)
            )

    # ─── helpers ─────────────────────────────────────────────────
    def _stop_robot(self):
        self.twist_cmd.linear.x = self.lin_vel_zero
        self.twist_cmd.angular.z = self.ang_vel_zero

    def _publish(self):
        # Clamp outputs
        self.twist_cmd.linear.x = max(
            min(self.twist_cmd.linear.x, self.lin_vel_fast), -self.lin_vel_fast)
        self.twist_cmd.angular.z = max(
            min(self.twist_cmd.angular.z, self.ang_vel_max), -self.ang_vel_max)
        self.cmd_vel_pub.publish(self.twist_cmd)

    def _print_info(self):
        self.get_logger().info(
            "Scan  L:%0.3f  F:%0.3f  R:%0.3f" %
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
            "roll_rad": roll_rad, "roll_deg": roll_rad * 180 * self.pi_inv,
            "pitch_rad": pitch_rad, "pitch_deg": pitch_rad * 180 * self.pi_inv,
            "yaw_rad": yaw_rad, "yaw_deg": yaw_rad * 180 * self.pi_inv,
        }


# ─────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = WallFollowerPD()
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
        node.get_logger().info("Wall Follower PD stopped.")
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()