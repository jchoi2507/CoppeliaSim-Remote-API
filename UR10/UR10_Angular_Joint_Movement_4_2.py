# 6/8/2021 Jacob Choi

# To include in lua script in Coppelia software:
# simRemoteApi.start(19999)

import sim
import matplotlib.pyplot
import numpy as np
import time
import sys

sim.simxFinish(-1) # Ends any existing communication threads
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5) # Parameters: Server IP, Port #,
                                                                  # boolean wait-until-connected
                                                                  # boolean doNotReconnectOnceDisconnected, timeOutinMs,
                                                                  # commThreadCycleinMs (usually set as 5)

# Prints out a successful/unsuccessful connection message
def connection_message(x):
    if x != -1:
        print("Connected to remote API server")
    else:
        print("Connection unsuccessful :(")
        sys.exit()

connection_message(clientID)

## UR10 JOINT SETTINGS ##

# BODY IS DYNAMIC:

# UR10
# UR10_link2
# UR10_link3
# UR10_link4
# UR10_link5
# UR10_link6

# MOTOR ENABLED + CONTROL LOOP ENABLED *:

# UR10_JOINT1
# UR10_JOINT2
# UR10_JOINT3
# UR10_JOINT4
# UR10_JOINT5
# UR10_JOINT6

                                                    ## JOINT POSITIONS ##

PI = np.pi

# Initializing + Calling Functions
joint_handle_array = [] # List of joint handles
joint_targetpos_array = [] # Target positions

# Initializes joint_handle_array with actual handle values -- RUN ONCE
def handle_array():
    for i in range(6):
        errorCode, joint_handle = sim.simxGetObjectHandle(clientID, "UR10_joint" + str(i + 1), sim.simx_opmode_blocking) # change operation mode if it doesn't work
        joint_handle_array.append(joint_handle)

# Initializes joint_targetpos_array with actual target position values -- RUN EVERY TIME AFTER MOVING
def targetpos_array():
    for i in range(6):
        k = input("Enter angle in degrees of joint " + str(i + 1) + "'s rotation ('quit'/'reset')")
        if k == "quit":
            return "quit"
            break
        elif k == "reset":
            return "reset"
            break
        else:
            k2 = float(k) * float(PI/180)
            joint_targetpos_array.append(k2)

# Signalling simulation to actually perform the changes
def move():
    for i in range(6):
        sim.simxSetJointTargetPosition(clientID, joint_handle_array[i], joint_targetpos_array[i], sim.simx_opmode_blocking)
        time.sleep(2)

# Function that brings the UR10 arm back to its original place
def reset():
    for i in range(6):
        sim.simxSetJointTargetPosition(clientID, joint_handle_array[i], 0, sim.simx_opmode_blocking)
        time.sleep(2)

# Looping the script
handle_array()
while True:
    a = targetpos_array()
    if a == "quit":
        joint_targetpos_array.clear()
        joint_handle_array.clear()
        break
    elif a == "reset":
        reset()
        joint_targetpos_array.clear()
    else:
        move()
        joint_targetpos_array.clear()
    print("\n")
