# 6/15/2021 Jacob Choi

# To include in lua script in Coppelia software:
# simRemoteApi.start(19999)

import sim
import matplotlib.pyplot
import numpy as np
import time
import sys

sim.simxFinish(-1)  # Ends any existing communication threads
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)  # Server IP, Port #, boolean wait-until-connected
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

PI = np.pi

# Gripper function that opens/closes the gripper
def gripper_function(clientid, closing, j1, j2, p1, p2):
    errorCode, p1 = sim.simxGetJointPosition(clientid, j1, sim.simx_opmode_buffer)
    errorCode, p2 = sim.simxGetJointPosition(clientid, j2, sim.simx_opmode_buffer)

    if closing == 1:
        if p1 < (p2 - 0.008):
            sim.simxSetJointTargetVelocity(clientid, j1, -0.1, sim.simx_opmode_oneshot) #Try sim.simx_opmode_streaming if it doesn't work
            sim.simxSetJointTargetVelocity(clientid, j2, -0.4, sim.simx_opmode_oneshot)
        else:
            sim.simxSetJointTargetVelocity(clientid, j1, -0.4, sim.simx_opmode_oneshot)
            sim.simxSetJointTargetVelocity(clientid, j2, -0.4, sim.simx_opmode_oneshot)

    else:
        if p1 < p2:
            sim.simxSetJointTargetVelocity(clientid, j1, 0.4, sim.simx_opmode_oneshot)
            sim.simxSetJointTargetVelocity(clientid, j2, 0.2, sim.simx_opmode_oneshot)
        else:
            sim.simxSetJointTargetVelocity(clientid, j1, 0.2, sim.simx_opmode_oneshot)
            sim.simxSetJointTargetVelocity(clientid, j2, 0.4, sim.simx_opmode_oneshot)

# The below function will stop moving the gripper, thus achieving 'fake gripping'
def pause_gripper(clientid, j1, j2):
    sim.simxSetJointTargetVelocity(clientid, j1, 0, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientid, j2, 0, sim.simx_opmode_oneshot)

# Simply opens the gripper at the start, as the gripper in my scene is closed at the beginning of simulation.
# Feel free to turn off if the gripper is already in an open position
def openGripperAtStart(clientid, j1, j2, p1, p2):
    errorCode, p1 = sim.simxGetJointPosition(clientid, j1, sim.simx_opmode_buffer)
    errorCode, p2 = sim.simxGetJointPosition(clientid, j2, sim.simx_opmode_buffer)

    if p1 < p2:
        sim.simxSetJointTargetVelocity(clientid, j1, 0.4, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(clientid, j2, 0.2, sim.simx_opmode_oneshot)
    else:
        sim.simxSetJointTargetVelocity(clientid, j1, 0.2, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(clientid, j2, 0.4, sim.simx_opmode_oneshot)

# Same exact move_L function as in the linear joint movement script for the UR10, basically sets coordinates
# for the target dummy. IK will then make the tip dummy (that is attached to the flange) to follow the target dummy
def move_L(clientid, target, target_pos, speed):
    returnCode, pos = sim.simxGetObjectPosition(clientid, target, -1, sim.simx_opmode_streaming)
    returnCode, pos = sim.simxGetObjectPosition(clientid, target, -1,
                                                sim.simx_opmode_buffer)

    returnCode, orient = sim.simxGetObjectOrientation(clientid, target, -1, sim.simx_opmode_streaming)
    returnCode, orient = sim.simxGetObjectOrientation(clientid, target, -1, sim.simx_opmode_buffer)

    for i in range(3):
        pos[i] = float(pos[i])
        orient[i] = float(orient[i])

    old_pos = []
    old_orient = []
    delta_pos = []
    delta_orient = []
    intermediate_pos = [0, 0, 0]
    intermediate_orient = [0, 0, 0]
    # target_pos = [1.5, 2, 5] ## TEST

    for i in range(3):
        if abs(target_pos[i + 3]) - orient[i] > PI and orient[i] < 0:
            orient[i] = orient[i] + 2*PI
        elif abs(target_pos[i + 3]) - orient[i] > PI and orient[i] > 0:
            orient[i] = orient[i] - 2*PI

    for i in range(3):
        old_pos.append(pos[i])
        delta_pos.append(target_pos[i] - old_pos[i])
        old_orient.append(orient[i])
        delta_orient.append(target_pos[i + 3] - old_orient[i])

    distance = np.linalg.norm(delta_pos)
    samples_number = round(distance * 50)

    for i in range(samples_number):
        for j in range(3):
            intermediate_pos[j] = (old_pos[j] + (delta_pos[j] / samples_number))
            intermediate_orient[j] = (old_orient[j] + (delta_orient[j] / samples_number))

        sim.simxSetObjectPosition(clientid, target, -1, intermediate_pos, sim.simx_opmode_oneshot)
        sim.simxSetObjectOrientation(clientid, target, -1, intermediate_orient, sim.simx_opmode_oneshot)

        for k in range(3):
            old_pos[k] = intermediate_pos[k]
            old_orient[k] = intermediate_orient[k]

        for k in range(3):
            intermediate_pos[k] = 0
            intermediate_orient[k] = 0

    old_pos.clear()
    delta_pos.clear()
    intermediate_pos.clear()

# Initializing
errorCode, target = sim.simxGetObjectHandle(clientID, 'target', sim.simx_opmode_blocking)
errorCode, j1 = sim.simxGetObjectHandle(clientID, 'ROBOTIQ_85_active1', sim.simx_opmode_blocking)
errorCode, j2 = sim.simxGetObjectHandle(clientID, 'ROBOTIQ_85_active2', sim.simx_opmode_blocking)
errorCode, p1 = sim.simxGetJointPosition(clientID, j1, sim.simx_opmode_streaming)
errorCode, p2 = sim.simxGetJointPosition(clientID, j2, sim.simx_opmode_streaming)

# Coordinates for basket 1
b1_initial_pos = [-1.85, 0.4, 0.45, 0, 0, 0]
b1_int_pos = [-1.85, 0.4, 0.6, 0, 0, 0]
b1_int_pos_2 = [-1.85, 0.75, 0.6, 0, 0, 0]
b1_int_pos_3 = [-1.85, 1.075, 0.6, 0, 0, 0]
b1_final_pos = [-1.85, 1.075, 0.525, 0, 0, 0]

b1_b2_transition_pos = [-1.85, 0.55, 0.6, 0, 0, 0]

# Coordinates for basket 2
b2_initial_pos = [-1.85, 0.575, 0.45, 0, 0, 0]
b2_int_pos = [-1.85, 0.575, 0.6, 0, 0, 0]
b2_int_pos_2 = [-1.85, 0.85, 0.6, 0, 0, 0]
b2_final_pos = [-1.85, 0.85, 0.525, 0, 0, 0] # Configure

errorCode, basket1 = sim.simxGetObjectHandle(clientID, 'Cuboid1', sim.simx_opmode_blocking)
errorCode, basket2 = sim.simxGetObjectHandle(clientID, 'Cuboid2', sim.simx_opmode_blocking)
errorCode, connector = sim.simxGetObjectHandle(clientID, 'ROBOTIQ_85_attachPoint', sim.simx_opmode_blocking)

# Functions that perform the movements of the cuboids/baskets
def moveBasket1():

    # Moving to initial position
    move_L(clientID, target, b1_initial_pos, 2)
    time.sleep(2)
    sim.simxSetObjectParent(clientID, basket1, connector, False, sim.simx_opmode_blocking)

    # Closing gripper
    gripper_function(clientID, 1, j1, j2, p1, p2)
    time.sleep(1)
    pause_gripper(clientID, j1, j2)
    time.sleep(1)

    # Moving object to second table
    move_L(clientID, target, b1_int_pos, 2)
    time.sleep(1)
    move_L(clientID, target, b1_int_pos_2, 2)
    time.sleep(1)
    move_L(clientID, target, b1_int_pos_3, 2)
    time.sleep(1)
    move_L(clientID, target, b1_final_pos, 2)
    time.sleep(1)
    sim.simxSetObjectParent(clientID, basket1, -1, False, sim.simx_opmode_blocking)
    gripper_function(clientID, 0, j1, j2, p1, p2)

    # Moving robotic arm back to first table, ready to move basket #2
    #move_L(clientID, target, b1_final_pos_2, 2)
    time.sleep(1)
    move_L(clientID, target, b1_int_pos_3, 2)
    time.sleep(1)
    move_L(clientID, target, b1_int_pos_2, 2)
    time.sleep(1)
    move_L(clientID, target, b1_b2_transition_pos, 2)
    time.sleep(1)

def moveBasket2():

    # Moving to initial position
    move_L(clientID, target, b2_initial_pos, 2)
    time.sleep(1)
    sim.simxSetObjectParent(clientID, basket2, connector, False, sim.simx_opmode_blocking)

    # Closing gripper
    gripper_function(clientID, 1, j1, j2, p1, p2)
    time.sleep(1)
    pause_gripper(clientID, j1, j2)
    time.sleep(1)

    # Moving object to second table
    move_L(clientID, target, b2_int_pos, 2)
    time.sleep(1)
    move_L(clientID, target, b2_int_pos_2, 2)
    time.sleep(1)
    move_L(clientID, target, b2_final_pos, 2)
    time.sleep(1)
    sim.simxSetObjectParent(clientID, basket2, -1, False, sim.simx_opmode_blocking)
    gripper_function(clientID, 0, j1, j2, p1, p2)

    # Moving robotic arm back to original position
    time.sleep(1)
    move_L(clientID, target, b2_int_pos_2, 2)
    time.sleep(10)

openGripperAtStart(clientID, j1, j2, p1, p2)
time.sleep(2)
moveBasket1()
moveBasket2()
