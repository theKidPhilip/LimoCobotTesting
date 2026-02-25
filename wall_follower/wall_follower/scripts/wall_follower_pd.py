def scan_callback(self, scan_msg: LaserScan):
    # ---------- First message: initialize geometry/index ranges ----------
    if not self.scan_info_done:
        self.scan_angle_min = scan_msg.angle_min
        self.scan_angle_max = scan_msg.angle_max
        self.scan_range_min = scan_msg.range_min
        self.scan_range_max = scan_msg.range_max
        self.scan_ranges_size = len(scan_msg.ranges)

        # total scan angle in degrees (approx)
        self.scan_angle_range = int(
            (abs(self.scan_angle_min) + abs(self.scan_angle_max)) * (180.0 / self.pi)
        )

        # degrees per index step
        self.scan_angle_inc = (self.scan_angle_range / self.scan_ranges_size)

        # center index = forward
        self.scan_front_index = int(self.scan_ranges_size / 2)

        # +/- 90 degrees indices (right/left)
        self.scan_right_index = int(self.scan_front_index - int(90.0 / self.scan_angle_inc))
        self.scan_left_index  = int(self.scan_front_index + int(90.0 / self.scan_angle_inc))

        # helper to clamp indices into valid range
        def clamp(i: int) -> int:
            return max(0, min(self.scan_ranges_size - 1, i))

        # sector half-width in indices
        front_half = int(self.scan_front_angle_range / self.scan_angle_inc)
        side_half  = int(self.scan_sides_angle_range / self.scan_angle_inc)

        # compute sector bounds
        self.scan_front_range_from_index = clamp(self.scan_front_index - front_half)
        self.scan_front_range_to_index   = clamp(self.scan_front_index + front_half)

        self.scan_right_range_from_index = clamp(self.scan_right_index - side_half)
        self.scan_right_range_to_index   = clamp(self.scan_right_index + side_half)

        self.scan_left_range_from_index  = clamp(self.scan_left_index - side_half)
        self.scan_left_range_to_index    = clamp(self.scan_left_index + side_half)

        self.scan_info_done = True

        self.get_logger().info("~~~~~ Start Scan Info ~~~~")
        self.get_logger().info(f"angles(rad): min={self.scan_angle_min:+0.3f} max={self.scan_angle_max:+0.3f}")
        self.get_logger().info(f"range(m):   min={self.scan_range_min:+0.3f} max={self.scan_range_max:+0.3f}")
        self.get_logger().info(f"ranges_size: {self.scan_ranges_size}")
        self.get_logger().info(f"front idx={self.scan_front_index}  range={self.scan_front_range_from_index}->{self.scan_front_range_to_index}")
        self.get_logger().info(f"right idx={self.scan_right_index}  range={self.scan_right_range_from_index}->{self.scan_right_range_to_index}")
        self.get_logger().info(f"left  idx={self.scan_left_index}   range={self.scan_left_range_from_index}->{self.scan_left_range_to_index}")
        self.get_logger().info("~~~~~ End Scan Info ~~~~")
        return

    # ---------- Utility: validate readings ----------
    def valid(r: float) -> bool:
        # Many real lidars output 0.0 when invalid
        return (not math.isinf(r)) and (not math.isnan(r)) and (r > 0.0)

    # ---------- Utility: get sector values ----------
    def sector_values(start_i: int, end_i: int):
        vals = []
        # inclusive bounds
        for i in range(start_i, end_i + 1):
            r = scan_msg.ranges[i]
            if valid(r):
                vals.append(r)
        return vals

    right_vals = sector_values(self.scan_right_range_from_index, self.scan_right_range_to_index)
    front_vals = sector_values(self.scan_front_range_from_index, self.scan_front_range_to_index)
    left_vals  = sector_values(self.scan_left_range_from_index,  self.scan_left_range_to_index)

    # ---------- Compute distances (meters) ----------
    if algo_choice == "avg":
        self.scan_right_range = (sum(right_vals) / len(right_vals)) if right_vals else self.scan_range_max
        self.scan_front_range = (sum(front_vals) / len(front_vals)) if front_vals else self.scan_range_max
        self.scan_left_range  = (sum(left_vals)  / len(left_vals))  if left_vals  else self.scan_range_max
    else:
        # MIN behavior (robust)
        self.scan_right_range = min(right_vals) if right_vals else self.scan_range_max
        self.scan_front_range = min(front_vals) if front_vals else self.scan_range_max
        self.scan_left_range  = min(left_vals)  if left_vals  else self.scan_range_max

    # Optional debug (uncomment if you want to compare quickly)
    # self.get_logger().info(
    #     f"RAW stats: min={min(scan_msg.ranges):.3f} max={max(scan_msg.ranges):.3f} (meters)"
    # )