import sys
sys.path.append("/Users/momodoubah/research/catkin_ws/src/mitad/src")
from utility.turn import findAngle, getMagnitude
import requests
import math
# from tf.transformations import euler_from_quaternion
# import rospy
import json

# url = "https://turtlebotrender.momodoubah1.repl.co/"
url = "http://localhost:9000/"

def fuseObjects (obj1, obj2):
    new = {}
    for item in obj1:
        new[item] = obj1[item]
    for item in obj2:
        new[item] = obj2[item]        
    return new

def manageNewTarget(response, stepDetails):
    if 'target' not in response:
        return
    data = response['target']
    if data == None or type(data) != str:
        return
    items = [int(x) for x in data.split(':')]
    if len(items) != 2:
        return

    tu = (items[0], items[1])
    if tu != stepDetails['end']:
        stepDetails['end'] = tu
        stepDetails['mode'] = 'route'

def getAreaMeta (blockers, areaSize):
    areaMeta = {}
    for key in blockers:
        x = math.floor((key[0])/areaSize)
        y = math.floor((key[1])/areaSize)
        id = (x,y)
        if id in areaMeta:
            areaMeta[id][key] = None
        else:
            areaMeta[id] = {}
            areaMeta[id][key] = None

    return areaMeta

def convertIntoKeysRaw(item):
    fresh = {}
    for child in item:
        idChild_ = f'{child[0]}:{child[1]}'
        fresh[idChild_] = None

    return fresh

def convertIntoKeys(item):
    fresh = {}
    for key in item:
        for child in item[key]:
            idChild_ = f'{child[0]}:{child[1]}'
            fresh[idChild_] = item[key][child]

    return fresh

def convertIntoTupleKeysArray(item):
    fresh = []
    for key in item:
        for child in item[key]:
            fresh.append(child)            

    return fresh    


def getTargetDirection(stepDetails):
    if 'index' not in stepDetails:
        return 0
    size = len(stepDetails['steps'])
    if stepDetails['index'] < 1 or stepDetails['index'] >= size:
        return 0
    curr = stepDetails['steps'][stepDetails['index']]
    prev = stepDetails['steps'][stepDetails['index']-1]
    resultant = (curr[0] - prev[0], curr[1] - prev[1])
    hypotenuse = getMagnitude(resultant)
    if hypotenuse == 0:
        return 0
    return math.acos(resultant[0]/hypotenuse)


def send(stepDetails, currentPosition, barriers):
    if currentPosition == None:
        return
    try:
        data = {'facingAngle': currentPosition[2], 'targetAngle': getTargetDirection(stepDetails), 'blockers': convertIntoKeys(barriers),
                    'visits': convertIntoKeys(stepDetails['visited']), 'path': stepDetails['steps'], 'robotPosition': currentPosition[3]}
        response = requests.post(url, json=data)
        manageNewTarget(json.loads(response.text), stepDetails)
    except:
        pass

def sendRaw(stepDetails, currentPosition, barriers, convertBarriers=False):

    data = {'facingAngle': currentPosition[2], 'targetAngle': getTargetDirection(stepDetails), 'blockers': convertIntoKeysRaw(barriers) if convertBarriers else barriers,
                    'visits': stepDetails['visited'], 'path': stepDetails['steps'], 'robotPosition': currentPosition[3]}
    requests.post(url, json= data)
        # manageNewTarget(json.loads(response.text), stepDetails)


def inBucket(item, bucket, areaSize, blockSize, justCheckParent=False, returnParentID=False):

    parentId = reverseApproximateCords(item, blockSize)
    parentId = approximateCords(parentId, areaSize)
    """
        Only return tuple if item not in list but you want to know the parentID
        Used for mg6 on emptyArea variable
    """
    if not (parentId in bucket):
        if returnParentID:
            return ( False, parentId ) 
        return False
    """
        This is just for checking that the parent is in the bucket
    """
    if justCheckParent:
        if returnParentID:
            return parentId
        return True

    return item in bucket[parentId]


def addNode(item, bucket, areaSize, blockSize):
    parentId = reverseApproximateCords(item, blockSize)
    parentId = approximateCords(item, areaSize)
    if not (parentId in bucket):
        bucket[parentId] = {}
    bucket[parentId][item] = None


def commentBarriers(barriers):
    rospy.loginfo('------------------------------\n')
    if len(barriers):
        for parent in barriers:
            rospy.loginfo(str(parent)+':')
            [rospy.loginfo(f'   {x}') for x in barriers[parent]]
            rospy.loginfo(' ')

    else:
        rospy.loginfo('empty')


def isInArea(target, currentPosition):

    if currentPosition == None or len(currentPosition) != 4:
        return False

    return target[0] == currentPosition[3][0] and target[1] == currentPosition[3][1]


def getEuler(quaternion):
    lst = [quaternion.x, quaternion.y, quaternion.z, quaternion.w]
    data = euler_from_quaternion(lst)
    return data


def cordsOkay(cords):
    if type(cords) != tuple:
        return False
    if len(cords) != 2:
        return False
    return True


def mitadFloor(number):
    pos = abs(number)
    isPositive = pos == number
    floored = math.floor(pos)
    return floored if isPositive else (floored * -1)


def reverseApproximateCords(cords, blockSize):
    if not cordsOkay(cords):
        return (0, 0)
    return (cords[0]*blockSize, cords[1]*blockSize)


def approximateCords(cords, blockSize):
    if cords == None:
        return (0, 0)
    return (mitadFloor(cords[0]/blockSize), mitadFloor(cords[1]/blockSize))

def getParentCords (cords, areaSize, blockSize):
    originalCords = reverseApproximateCords(cords, blockSize)
    return approximateCords(originalCords, areaSize)

def identifyVelocities(frequency, stepDetails, currentPosition, robotYaw):

    index = stepDetails['index']
    mode = stepDetails['mode']
    steps = stepDetails['steps']

    start = rospy.get_time()
    if index >= len(steps) or currentPosition == None or mode == 'route':
        # rospy.loginfo('early termination 1')
        return {'z': 0, 'x': 0, 'angle': 0}

    if currentPosition[3] not in stepDetails['steps']:
        # rospy.loginfo('early termination 2')
        stepDetails['mode'] = 'route'
        return {'z': 0, 'x': 0, 'angle': 0}

    current = steps[index]
    prev = steps[index-1] if index >= 1 else (0, 0)
    direction = (current[0] - prev[0], current[1] - prev[1])
    angle = findAngle(robotYaw, direction)
    duration = rospy.get_time() - start
    remaining = (1/frequency) - duration
    speed = angle / remaining

    if mode == 'turn':
        if abs(angle) < 1e-1:
            mode = 'move'
            speed = 0
        else:
            speed = speed*0.2

    elif isInArea(steps[index], currentPosition):
        rospy.loginfo(f'We have reached {steps[index]}')
        mode = 'turn'
        index += 1
        if index >= len(steps):
            rospy.loginfo(f'The end')
            stepDetails['end'] = None
            # exit()

    stepDetails['index'] = index
    stepDetails['mode'] = mode
    stepDetails['steps'] = steps
    # rospy.loginfo(
    #     f'Going for rotation:{speed} with vel: {0.4 if mode == "move" else 0}')

    return {'z': speed, 'x': 1 if mode == 'move' else 0, 'angle': angle}
