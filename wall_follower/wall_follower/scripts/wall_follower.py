#!/usr/bin/env python3
"""
Wall follower node (AUTO-RUN, no keyboard).

Subscribes:
  /scan  (sensor_msgs/LaserScan)

Publishes:
  /cmd_vel (geometry_msgs/Twist)
"""

import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


def _finite(x: float) -> bool:
    return (not math.isinf(x)) and (not math.isnan(x))


class WallFollower(Node):
    def __init__(self):
        super().__init__("wall_follower")

        # ---------------- Parameters ----------------
        self.declare_parameter("side_choice", "none")   # "left" / "right" / "none"
        self.declare_parameter("algo_choice", "min")    # "min" / "avg"
        self.declare_parameter("control_hz", 10.0)

        self.declare_parameter("robot_radius", 0.10)
        self.declare_parameter("side_gap_min", 0.05)    # + radius
        self.declare_parameter("side_gap_max", 0.10)    # + radius
        self.declare_parameter("front_gap", 0.40)       # + radius

        self.declare_parameter("lin_slow", 0.10)
        self.declare_parameter("lin_fast", 0.20)        # safer on real robot
        self.declare_parameter("ang_slow", 0.08)
        self.declare_parameter("ang_fast", 0.50)

        self.declare_parameter("max_lin", 0.20)
        self.declare_parameter("max_ang", 0.80)

        self.declare_parameter("front_window_deg", 15.0)
        self.declare_parameter("side_window_deg", 15.0)

        # ---------------- Load params ----------------
        self.side_choice = str(self.get_parameter("side_choice").value).lower()
        self.algo_choice = str(self.get_parameter("algo_choice").value).lower()

        rr = float(self.get_parameter("robot_radius").value)
        self.side_threshold_min = rr + float(self.get_parameter("side_gap_min").value)
        self.side_threshold_max = rr + float(self.get_parameter("side_gap_max").value)
        self.front_threshold = rr + float(self.get_parameter("front_gap").value)

        self.lin_slow = float(self.get_parameter("lin_slow").value)
        self.lin_fast = float(self.get_parameter("lin_fast").value)
        self.ang_slow = float(self.get_parameter("ang_slow").value)
        self.ang_fast = float(self.get_parameter("ang_fast").value)

        self.max_lin = float(self.get_parameter("max_lin").value)
        self.max_ang = float(self.get_parameter("max_ang").value)

        self.front_window_deg = float(self.get_parameter("front_window_deg").value)
        self.side_window_deg = float(self.get_parameter("side_window_deg").value)

        # Angular multiplier based on algo (matches your old logic idea)
        self.ang_vel_mult = 1.25 if self.algo_choice == "min" else 3.0

        # ---------------- ROS interfaces ----------------
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            durability=DurabilityPolicy.VOLATILE,
        )

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.scan_sub = self.create_subscription(LaserScan, "/scan", self.scan_cb, qos)

        # ---------------- State ----------------
        self.have_scan = False
        self.wall_found = False
        self.side_chosen = "none"

        self.scan_left = 10.0
        self.scan_front = 10.0
        self.scan_right = 10.0

        self.twist = Twist()

        hz = float(self.get_parameter("control_hz").value)
        self.timer = self.create_timer(1.0 / max(hz, 1.0), self.control_loop)

        self.get_logger().info("WallFollower started (AUTO-RUN).")
        self.get_logger().info(f"side_choice={self.side_choice}, algo_choice={self.algo_choice}")

    def scan_cb(self, msg: LaserScan):
        def angle_to_index(angle_rad: float) -> int:
            if msg.angle_increment == 0.0:
                return 0
            i = int(round((angle_rad - msg.angle_min) / msg.angle_increment))
            return max(0, min(i, len(msg.ranges) - 1))

        def window_value(center_rad: float, half_window_deg: float, mode: str) -> float:
            half = math.radians(half_window_deg)
            i0 = angle_to_index(center_rad - half)
            i1 = angle_to_index(center_rad + half)
            if i1 < i0:
                i0, i1 = i1, i0

            vals = [msg.ranges[i] for i in range(i0, i1 + 1) if _finite(msg.ranges[i])]
            if not vals:
                # if nothing finite, return something "far"
                return msg.range_max if _finite(msg.range_max) else 10.0

            return (sum(vals) / len(vals)) if mode == "avg" else min(vals)

        mode = "avg" if self.algo_choice == "avg" else "min"

        self.scan_front = window_value(0.0, self.front_window_deg, mode)
        self.scan_right = window_value(-math.pi / 2.0, self.side_window_deg, mode)
        self.scan_left = window_value(+math.pi / 2.0, self.side_window_deg, mode)

        self.have_scan = True

    def control_loop(self):
        if not self.have_scan:
            return

        lin = 0.0
        ang = 0.0

        if not self.wall_found:
            # move forward until we detect a wall in front
            if self.scan_front < self.front_threshold:
                self.wall_found = True

                # choose side
                if self.side_choice in ("left", "right"):
                    self.side_chosen = self.side_choice
                else:
                    self.side_chosen = "right" if (self.scan_right < self.scan_left) else "left"

                self.get_logger().info(f"Wall found. Following on: {self.side_chosen}")
                lin = 0.0
                ang = 0.0
            else:
                lin = self.lin_slow
                ang = 0.0

        else:
            # obstacle/wall in front -> turn away while creeping forward
            if self.scan_front < self.front_threshold:
                lin = self.lin_slow
                if self.side_chosen == "right":
                    ang = +self.ang_fast * self.ang_vel_mult  # turn left
                else:
                    ang = -self.ang_fast * self.ang_vel_mult  # turn right
            else:
                # follow wall by keeping distance in a band
                lin = self.lin_fast
                if self.side_chosen == "right":
                    if self.scan_right < self.side_threshold_min:
                        ang = +self.ang_slow
                    elif self.scan_right > self.side_threshold_max:
                        ang = -self.ang_slow
                    else:
                        ang = 0.0
                else:
                    if self.scan_left < self.side_threshold_min:
                        ang = -self.ang_slow
                    elif self.scan_left > self.side_threshold_max:
                        ang = +self.ang_slow
                    else:
                        ang = 0.0

        # clamp
        lin = max(-self.max_lin, min(self.max_lin, lin))
        ang = max(-self.max_ang, min(self.max_ang, ang))

        self.twist.linear.x = float(lin)
        self.twist.angular.z = float(ang)
        self.cmd_pub.publish(self.twist)


def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # stop on exit
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()