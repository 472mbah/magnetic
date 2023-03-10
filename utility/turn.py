import math


def getMagnitude(vector):
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))


def getDistance(vectorOne, vectorTwo, pythagoras=True):
    if not pythagoras:
        return abs(vectorOne[0]-vectorTwo[0]) + abs(vectorOne[1]-vectorTwo[1])  
    return math.sqrt(math.pow(vectorOne[0]-vectorTwo[0], 2) + math.pow(vectorOne[1]-vectorTwo[1], 2))


def getQuadrant(vector):
    if vector[0] >= 0 and vector[1] >= 0:
        return 1
    if vector[0] <= 0 and vector[1] >= 0:
        return 2
    if vector[0] <= 0 and vector[1] <= 0:
        return 3

    return 4


def translateCurrentAngle(currentAngle):
    if currentAngle >= 0:
        return currentAngle
    else:
        return (2*math.pi) + currentAngle


def translateTargetVector(targetVector):
    magnitude = getMagnitude(targetVector)
    if magnitude == 0:
        return 0
    quadrant = getQuadrant(targetVector)
    treatAngle = math.acos(targetVector[0] / magnitude)
    #treatAngle = treatAngle * (180/math.pi)

    if quadrant == 1:
        return treatAngle
    if quadrant == 2:
        return treatAngle
    # if quadrant==3:
    #	return 360 - treatAngle
    else:
        return (2*math.pi) - treatAngle

def findVectorDifference (vectorA, vectorB):
    return (vectorA[0]-vectorB[0], vectorA[1]-vectorB[1])

def convertVectorToAngle (vector):
    if vector[1] == 0:
        return 0
    rads = math.acos(vector[0]/vector[1])
    return rads * (180/math.pi)

"""
Current angle follows model where anything beyound pi 
radius becomes the negative of its reflected value
"""

def findAngle(currentAngle, targetVector):
    turtlebotAngle = translateCurrentAngle(currentAngle)
    targetAngle = translateTargetVector(targetVector)
    sweepAngle = targetAngle - turtlebotAngle
    absVersion = abs(sweepAngle)
    if absVersion <= math.pi:
        return sweepAngle

    inverseAngle = (2*math.pi) - absVersion
    isNegative = absVersion == sweepAngle
    return (-1 if isNegative else 1) * inverseAngle


def interpretValue(currentAngle, targetVector):
    direction = findAngle(currentAngle, targetVector)
    absVersion = abs(direction)

    if direction > 0:
        go = 'Anticlockwise'
    else:
        go = 'Clockwise'

    return direction
    #print('sweep current', currentAngle, translateCurrentAngle(currentAngle))
    #print('sweep target', targetVector, translateTargetVector(targetVector))
    # print(f'Go {absVersion*180/math.pi} in the {go} direction, targetVector: {targetVector}, currentAngle: {currentAngle}')


# targetVector = (-3, 3)
# currentAngle = math.pi
#print(currentAngle, translateCurrentAngle(currentAngle))
#print(targetVector, getQuadrant(targetVector))
#print(targetVector, translateTargetVector(targetVector))
# interpretValue( currentAngle, targetVector  )
