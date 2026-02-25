#!/usr/bin/env python3
"""
arm_then_run_wall_follower.py (AUTO START)

Starts wall follower automatically after bringup launches.
No keyboard / no termios.

Also shuts it down cleanly when this process is stopped.
"""

import os
import signal
import subprocess
import time


def main() -> int:
    print("\n[blazerbot_bringup] LIMO is up.")
    print("[blazerbot_bringup] Auto-starting wall follower in 2 seconds...\n")

    time.sleep(2.0)

    proc = subprocess.Popen(
        ["ros2", "run", "blazerbot_wall_follower", "wall_follower_node"],
        stdout=None,
        stderr=None,
        preexec_fn=os.setsid,  # separate process group so we can SIGINT it
    )

    try:
        # Wait here so launch keeps this node alive
        return proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGINT)
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())