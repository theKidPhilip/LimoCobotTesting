#!/usr/bin/env python3
"""
Gate script for LAB SAFETY:
- Robot must NOT move until 'S' is pressed.
- After 'S', start the wall follower node.
- Press 'Q' to quit (before starting).
"""

import subprocess
import sys
import termios
import tty


def get_key() -> str:
    """Read one keypress (single character) without Enter."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)  # immediate key reads
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main() -> int:
    print("\n[blazerbot_bringup] LIMO is up.")
    print("[blazerbot_bringup] Press 'S' to START wall following.")
    print("[blazerbot_bringup] Press 'Q' to quit.\n")

    # Wait for S/Q
    while True:
        k = get_key()
        if k in ("s", "S"):
            break
        if k in ("q", "Q"):
            print("[blazerbot_bringup] Quit.")
            return 0

    print("[blazerbot_bringup] Starting wall follower...\n")

    # IMPORTANT: replace these with your actual package + executable names
    cmd = ["ros2", "run", "wall_follower", "wall_follower"]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())