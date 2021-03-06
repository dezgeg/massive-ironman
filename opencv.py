import cv
import cv2
import os
import sys
import atexit
import numpy

RED = cv.Scalar(0, 0, 255, 0)
BLUE = cv.Scalar(255, 0, 0, 0)
WHITE = cv.Scalar(255, 255, 255, 0)
YELLOW = cv.Scalar(0, 255, 255, 0)

BALL_SIZE_THRESHOLD = 50


def nothing(x):
    pass


# If '-t' flag given, don't actually send commands to the robot
if '-t' not in sys.argv:
    if not os.path.exists("/tmp/nxt"):
        print "No named pipe"
        sys.exit(1)
    tcpSocket = open('/tmp/nxt', 'w', 0)
else:
    tcpSocket = open('/dev/null', 'w')


def die():
    print "killing"
    tcpSocket.write(' ')  # stop


atexit.register(die)

cv2.namedWindow('X')
cv2.createTrackbar('H_min', 'X', 6, 255, nothing)
cv2.createTrackbar('S_min', 'X', 90, 255, nothing)
cv2.createTrackbar('V_min', 'X', 40, 255, nothing)
cv2.createTrackbar('H_max', 'X', 13, 255, nothing)
cv2.createTrackbar('S_max', 'X', 255, 255, nothing)
cv2.createTrackbar('V_max', 'X', 255, 255, nothing)

numSeenFrames = 0
paused = False
trackTarget = 'ball' # either 'ball' or 'home'
seekingHome = False

tcpSocket.write('3')  # set power
tcpSocket.write('-')  # open jaws

capture = cv2.VideoCapture(0)
while True:
    k = cv2.waitKey(1) & 0xFF
    if k == 32:  # Space
        paused = not paused
        if paused:
            tcpSocket.write(' ')  # stop
    if k == 27:  # Esc
        break

    ret, sourceImage = capture.read()

    # Camera is mounted upside down, rotate 180 degrees
    sourceImage = cv2.flip(sourceImage, 0)
    sourceImage = cv2.flip(sourceImage, 1)

    if trackTarget == 'ball':
        # Orange
        minHue = cv2.getTrackbarPos('H_min', 'X')
        maxHue = cv2.getTrackbarPos('H_max', 'X')
    else:
        # Light green
        minHue = 44
        maxHue = 54
    min_color = cv.Scalar(minHue,
                          cv2.getTrackbarPos('S_min', 'X'),
                          cv2.getTrackbarPos('V_min', 'X'), 0)
    max_color = cv.Scalar(maxHue,
                          cv2.getTrackbarPos('S_max', 'X'),
                          cv2.getTrackbarPos('V_max', 'X'), 0)

    # Find contours in the thresholded image
    thresholdImage = cv2.inRange(cv2.cvtColor(sourceImage, cv2.COLOR_BGR2HSV), min_color, max_color)
    contours, _ = cv2.findContours(thresholdImage.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    thresholdImage = cv2.cvtColor(thresholdImage, cv2.COLOR_GRAY2RGB)

    # Sort contours by sum of width+height of bounding box, also rejecting too small boxes
    boxes = []
    for c in contours:
        rect = cv2.boundingRect(c)
        width = rect[2]
        height = rect[3]
        widthHeightSum = width + height
        if widthHeightSum > BALL_SIZE_THRESHOLD:
            boxes.append((-widthHeightSum, rect))
    boxes.sort()

    if len(boxes) > 0:
        # Target found, draw its bounding box
        rect = boxes[0][1]
        widthHeightSum = -boxes[0][0]

        topLeft = rect[0:2]
        bottomRight = (rect[0] + rect[2], rect[1] + rect[3])
        ballPos = ((topLeft[0] + bottomRight[0]) / 2, (topLeft[1] + bottomRight[1]) / 2)

        cv2.rectangle(thresholdImage, topLeft, bottomRight, RED)
        cv2.circle(thresholdImage, ballPos, 3, cv.Scalar(0, 255, 0, 0))
        cv2.putText(thresholdImage, str(widthHeightSum), ballPos, cv2.FONT_HERSHEY_SIMPLEX, 1.0, RED, 2)
    else:
        # No target found
        ballPos = None
        widthHeightSum = None

    # Draw steering boundaries
    numBoundaries = 11
    height, width, _ = sourceImage.shape
    for i in xrange(1, numBoundaries):
        coord = int((float(i) / numBoundaries) * width)
        if i == numBoundaries / 2 or i == numBoundaries / 2 + 1:
            color = WHITE
        else:
            color = BLUE
        cv2.line(thresholdImage, (coord, 0), (coord, height), color)


    # Calculate steer
    if ballPos is None:
        steerDir = None
    else:
        steerDir = int(round((float(ballPos[0]) / width) * numBoundaries - float(numBoundaries) / 2))
    cv2.putText(thresholdImage, str(steerDir), (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, BLUE, 2)

    if paused:
        cv2.putText(thresholdImage, '-', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, RED, 2)
    elif not seekingHome:
        numSeenFrames += 1

        if numSeenFrames < 50:
            if ballPos is None:
                numSeenFrames = 0
        else:
            # If we have previously seen the ball for >= 50 consecutive frames, but don't see it anymore...
            if trackTarget == 'ball' and ballPos is None:
                # ... then we got the ball, start rotating in place to locate home position
                tcpSocket.write("+") # close jaws
                trackTarget = 'home'
                seekingHome = True

        # Send driving commands
        if steerDir is None:
            tcpSocket.write(' ')  # stop
        else:
            letter = chr(abs(steerDir) * 4 + ord('A') + (steerDir > 0))
            tcpSocket.write(letter)
    else:
        # Rotating in place, looking for home
        tcpSocket.write('e') # turn right
        if ballPos and widthHeightSum >= 150:
            # Located a suitable home place, now start driving towards it
            seekingHome = False

    # Resize images to fit on the screen
    resizeFactor = 0.75
    resizedThresholdImage = cv2.resize(thresholdImage, (int(width * resizeFactor), int(height * resizeFactor)))
    resizedSourceImage = cv2.resize(sourceImage, (int(width * resizeFactor), int(height * resizeFactor)))

    # Draw processed image & camera image side by side
    concatenatedImage = numpy.concatenate((resizedThresholdImage, resizedSourceImage), 1)
    cv2.imshow('X', concatenatedImage)
