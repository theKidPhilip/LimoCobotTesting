#
# File: delock.sh
# Project: scripts
# File Created: Thursday, 5th February 2026 5:12:07 PM
# Author: Zabdiel Addo
# Email: zabdiel.addo@ashesi.edu.gh
# Version: 1.0.0
# Brief: <<brief>>
# -----
# Last Modified: Thursday, 5th February 2026 5:13:04 PM
# Modified By: Zabdiel Addo
# -----
# Copyright ©2026 Zabdiel Addo
#

#!/bin/bash

sudo lsof /var/lib/dpkg/lock
sudo lsof /var/lib/dpkg/lock-frontend
sudo lsof /var/lib/apt/lists/lock

sudo rm /var/lib/dpkg/lock
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock

sudo dpkg --configure -a