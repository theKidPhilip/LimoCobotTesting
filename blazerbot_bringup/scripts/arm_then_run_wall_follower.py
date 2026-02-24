"""
File: arm_then_run_wall_follower.py
Project: lab-3-locomotion-and-sensing-limo-blazers
File Created: Tuesday, 24th February 2026 10:08:59 PM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Tuesday, 24th February 2026 10:09:14 PM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""

#!/usr/bin/env python3
"""
Wait for 'S' keypress, then run the wall follower node.

This satisfies the lab safety requirement: robot must NOT move until 'S' is pressed.
"""

import subprocess
import sys
import termios
import tty


def get_key() -> str:
    """Read one character from terminal without pressing Enter."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main() -> int:
    print("\n[blazerbot_bringup] LIMO is up. Press 'S' to START wall following.")
    print("[blazerbot_bringup] Press 'Q' to quit.\n")

    while True:
        key = get_key()
        if key in ("s", "S"):
            print("\n[blazerbot_bringup] Starting wall_follower_node...\n")
            return subprocess.call(
                ["ros2", "run", "blazerbot_wall_follower", "wall_follower_node"]
            )
        if key in ("q", "Q"):
            print("\n[blazerbot_bringup] Quit.\n")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())