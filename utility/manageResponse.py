from utility.util import approximateCords, getEuler, reverseApproximateCords
from utility.turn import getDistance
import math
import sys
# import rospy
sys.path.append("/Users/momodoubah/research/catkin_ws/src/mitad/src")


def responseToOdom(msg, currentPosition, initialPosition, blockSize):
    currentPosition = (msg.pose.pose.position.x,
                       msg.pose.pose.position.y, msg.pose.pose.position.z)

    currentPosition = (msg.pose.pose.position.x, msg.pose.pose.position.y,
                       msg.pose.pose.position.z, approximateCords(currentPosition, blockSize))

    angles = getEuler(msg.pose.pose.orientation)
    robotYaw = angles[2]

    if initialPosition == None:
        initialPosition = (msg.pose.pose.position.x,
                           msg.pose.pose.position.y, msg.pose.pose.position.z)

    return (currentPosition, initialPosition, robotYaw)


def responseToScan(msg, stepDetails, currentPosition, barriers, robotYaw, blockSize, areaSize):
    if currentPosition == None:
        return
    recentlySet = {}
    size = len(msg.ranges)
    offset = robotYaw

    lastIndex = -1

    for k in range(size):
        if msg.ranges[k] == float('inf'):
            continue
        if msg.ranges[k] > msg.range_max or msg.ranges[k] < msg.range_min:
            continue
        thetaT = ((k+1) * math.pi / 180) + offset
        y = math.sin(thetaT) * msg.ranges[k]
        x = math.cos(thetaT) * msg.ranges[k]
        y += currentPosition[1]
        x += currentPosition[0]

        combinedParent = approximateCords((x, y), areaSize)
        combinedChild = approximateCords((x, y), blockSize)

        if stepDetails['mode'] != 'route' and combinedChild in stepDetails['steps']:
            lastIndex = max(
                lastIndex, stepDetails['steps'].index(combinedChild))

        if combinedParent not in recentlySet and combinedParent in barriers:
            del barriers[combinedParent]
            recentlySet[combinedParent] = None

        if not combinedParent in barriers:
            barriers[combinedParent] = {combinedChild: 1}
        else:
            if combinedChild in barriers[combinedParent]:
                barriers[combinedParent][combinedChild] += 1
            else:
                barriers[combinedParent][combinedChild] = 1

    """
        To remove an area from our list, it must be within range and be in the list
    """

    toRemove = []

    for key in barriers:
        if key in recentlySet:
            continue
        approximated = reverseApproximateCords(key, areaSize)
        distance = getDistance(currentPosition, approximated)
        if distance < msg.range_max:
            toRemove.append(key)

    for item in toRemove:
        del barriers[item]

    return lastIndex
