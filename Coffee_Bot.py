#!/usr/bin/env python3

import evdev
import ev3dev.auto as ev3
import threading
import time

## Value Converters (for Joystick accuracy) ##
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def scale(val, src, dst):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    return scale(value,(0,255),(-1000,1000)) # 0-255 degrees --> -1000<=...>=1000 motor Power #

def dc_clamp(value):
    return clamp(value,-1000,1000)

## Start ##
print("Finding ps4 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
ps4dev = devices[0].fn

gamepad = evdev.InputDevice(ps4dev)

forward_speed = 0 ## Linear Velocity B,C ##
side_speed = 0 ## Rotation Speed B,C ##
spin_speed = 0 ## Motor Α Power ##
running = True
class MotorThread(threading.Thread):
    def __init__(self):
        ## Αρχικοποίηση Μοτέρ ##
        self.right_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        self.left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        self.front_motor = ev3.MediumMotor(ev3.OUTPUT_A)
        threading.Thread.__init__(self)

    def run(self):
        print("Engine running!")
        while running:
            self.front_motor.run_forever(speed_sp=dc_clamp(spin_speed*1.5))
            self.right_motor.run_forever(speed_sp=dc_clamp(forward_speed+side_speed))
            self.left_motor.run_forever(speed_sp=dc_clamp(-forward_speed+side_speed))
        self.right_motor.stop()
        self.left_motor.stop()
        self.front_motor.stop()

motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()

for event in gamepad.read_loop():   #Forever Loop
    if event.type == 3:             #A stick is moved
        if event.code == 0:         #Axis Χ for JoyStick
            forward_speed = -(scale_stick(event.value)/2)
        if event.code == 1:         #Axis Υ for JoyStick
            side_speed = -(scale_stick(event.value)/2)
        if side_speed < 100 and side_speed > -100:
            side_speed = 0
            spin_speed = 0
        if forward_speed < 100 and forward_speed > -100:
            forward_speed = 0
            spin_speed = 0
        
                 
            
    if event.type == 1 and event.code == 305 and event.value == 1:
        print("O button is pressed. Stopping...")
        running = False
        time.sleep(0.5) # Wait for the motor thread to finish
        break 
    if event.type == 1 and event.code == 307 and event.value ==1:
        spin_speed = (scale_stick(event.value)/6)
    if event.type == 1 and event.code == 304 and event.value ==1:
        spin_speed = -(scale_stick(event.value)/6)
    if event.type == 1 and event.code == 313 and event.value ==1:
        spin_speed = 0
    
               ## Manual ##
         ## X ---> Release grab ##
         ## Δ ---> Use the grab ##
         ## O ---> Exit Program ##
         ## RS ---> Motor movement ##
    ## -------Thanks For Playing------- ##
    