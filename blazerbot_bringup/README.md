```

Structure for `blazerbot_bringup`:
```

blazerbot_bringup/
├── config/
│   ├── limo_slam_params.yaml
│   └── limo_nav2_params.yaml
├── maps/
│   ├── limo_map.pgm      ← copied after mapping on physical robot
│   └── limo_map.yaml     ← copied after mapping on physical robot
├── launch/
│   └── robot_bringup.launch.py
├── CMakeLists.txt
└── package.xml


We'll create our own map using our code. Those existing maps in limo_bringup are from previous labs/projects and won't match the wall_arena environment.
The workflow on the physical Limo will be:
Step 1 — Map the wall_arena with our SLAM:
bashros2 launch blazerbot_bringup robot_bringup.launch.py mode:=mapping
Step 2 — Drive around wall_arena slowly with teleop:
bashros2 run teleop_twist_keyboard teleop_twist_keyboard
Step 3 — Save the map to blazerbot_bringup/maps/:
bashros2 run nav2_map_server map_saver_cli -f /path/to/blazerbot_bringup/maps/limo_map
Step 4 — Then navigate:
bashros2 launch blazerbot_bringup robot_bringup.launch.py mode:=navigation
So blazerbot_bringup/maps/ will hold the map we generate on the physical robot in the actual wall_arena. The limo_map.pgm and limo_map.yaml placeholders are just empty for now until you run mapping on the day.
Add a .gitkeep to the maps folder so git tracks it:
bashtouch blazerbot_bringup/maps/.gitkeep
echo "maps/*.pgm" >> .gitignore
echo "maps/*.yaml" >> .gitignore
