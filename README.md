[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/LBOJ36UH)



limo_ros2 …
➜ 

limo_ros2 on  testing [!?] …
➜ ros2 topic echo /limo_status --once
header:
  stamp:
    sec: 1
    nanosec: 772067603
  frame_id: ''
vehicle_state: 0
control_mode: 1
battery_voltage: 11.9
error_code: 0
motion_mode: 1
---

limo_ros2 took 2.2s …
➜ grep -R "MODE_FOUR_DIFF" -n limo_base                    
limo_base/include/limo_base/limo_protocol.h:98:    MODE_FOUR_DIFF = 0x00,
limo_base/src/limo_driver.cpp:472:            case MODE_FOUR_DIFF: {
limo_base/src/limo_driver.cpp:580:            case MODE_FOUR_DIFF: {

limo_ros2 on  testing [!?] …
➜ grep -R "CONFIG" -n limo_base        
limo_base/include/limo_base/limo_protocol.h:65:#define MSG_CTRL_MODE_CONFIG_ID 0x421
limo_base/src/limo_driver.cpp:418:        frame.id = MSG_CTRL_MODE_CONFIG_ID;

limo_ros2 …
➜ grep -R "0x4" -n limo_base/include/limo_base
limo_base/include/limo_base/limo_protocol.h:65:#define MSG_CTRL_MODE_CONFIG_ID 0x421

limo_ros2 …
➜ 