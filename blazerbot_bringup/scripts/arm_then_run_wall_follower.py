#!/usr/bin/env python3
"""
arm_then_run_wall_follower.py

Safety gate:
- Robot does NOT move until user presses 'S'
- Press 'Q' to quit (and stop the wall follower process)

Works even when launched via `ros2 launch` by reading keyboard from /dev/tty.
"""

import os
import signal
import subprocess
import sys
import termios
import tty


def _open_keyboard_stream():
    """
    Return a file-like object that supports termios.
    If stdin isn't a TTY (common in ros2 launch), use /dev/tty.
    """
    if sys.stdin.isatty():
        return sys.stdin
    # /dev/tty is the controlling terminal for the process
    return open("/dev/tty", "r")


def get_key(kbd_stream) -> str:
    """Read one character (no Enter needed)."""
    fd = kbd_stream.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = kbd_stream.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main() -> int:
    print("\n[blazerbot_bringup] LIMO is up.")
    print("[blazerbot_bringup] Press 'S' to START wall following.")
    print("[blazerbot_bringup] Press 'Q' to quit.\n")

    kbd = _open_keyboard_stream()
    proc = None

    try:
        while True:
            k = get_key(kbd).lower()

            if k == "s":
                if proc is None or proc.poll() is not None:
                    print("[blazerbot_bringup] Starting wall follower...")
                    # IMPORTANT: match your wall follower package + executable name
                    proc = subprocess.Popen(
                        ["ros2", "run", "blazerbot_wall_follower", "wall_follower_node"],
                        stdout=None,
                        stderr=None,
                        preexec_fn=os.setsid,  # separate process group
                    )
                else:
                    print("[blazerbot_bringup] Wall follower already running.")

            elif k == "q":
                print("[blazerbot_bringup] Quit requested.")
                break

    except KeyboardInterrupt:
        pass
    finally:
        # stop wall follower if running
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGINT)
            except Exception:
                pass

        try:
            if kbd is not sys.stdin:
                kbd.close()
        except Exception:
            pass

        print("[blazerbot_bringup] Exiting gate.\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())