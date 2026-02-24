#
# File: kill_ros.sh
# Project: scripts
# File Created: Thursday, 5th February 2026 5:12:18 PM
# Author: Zabdiel Addo
# Email: zabdiel.addo@ashesi.edu.gh
# Version: 1.0.0
# Brief: <<brief>>
# -----
# Last Modified: Thursday, 5th February 2026 5:13:15 PM
# Modified By: Zabdiel Addo
# -----
# Copyright ©2026 Zabdiel Addo
#

#!/bin/bash

ps aux | grep ros | grep -v grep | awk '{ print "kill -9", $2 }' | sh
echo "All ROS Processes Killed"

ps aux | grep gazebo | grep -v grep | awk '{ print "kill -9", $2 }' | sh
ps aux | grep gz | grep -v grep | awk '{ print "kill -9", $2 }' | sh
echo "All Gazebo Processes Killed"
