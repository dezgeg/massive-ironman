import cv
import cv2
import socket
import os
import sys


def nothing(x):
    pass

class SendableStdout:
    def send(self, s):
        print s

if True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 9001))
    s.listen(1)
    os.system('/home/tmtynkky/robo/massive-ironman/lejos/bin/nxjsocketproxy -u &')
    tcpSocket, addr = s.accept()
    tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
else:
    tcpSocket = SendableStdout()

cv2.namedWindow('X')
cv2.createTrackbar('H_min', 'X', 13, 255, nothing)
cv2.createTrackbar('S_min', 'X', 90, 255, nothing)
cv2.createTrackbar('V_min', 'X', 90, 255, nothing)
cv2.createTrackbar('H_max', 'X', 22, 255, nothing)
cv2.createTrackbar('S_max', 'X', 255, 255, nothing)
cv2.createTrackbar('V_max', 'X', 255, 255, nothing)

capture = cv2.VideoCapture(1)
try:
    while True:
        k = cv2.waitKey(1) & 0xFF
        if k != 255:
            break

        ret, sourceImg = capture.read()

        min_color = cv.Scalar(cv2.getTrackbarPos('H_min', 'X'),
                              cv2.getTrackbarPos('S_min', 'X'),
                              cv2.getTrackbarPos('V_min', 'X'), 0)
        max_color = cv.Scalar(cv2.getTrackbarPos('H_max', 'X'),
                              cv2.getTrackbarPos('S_max', 'X'),
                              cv2.getTrackbarPos('V_max', 'X'), 0)

        thresholdImage = cv2.inRange(cv2.cvtColor(sourceImg, cv2.COLOR_BGR2HSV), min_color, max_color)
        contours, foo = cv2.findContours(thresholdImage.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        thresholdImage = cv2.cvtColor(thresholdImage, cv2.COLOR_GRAY2RGB)

        boxes = []
        for c in contours:
            rect = cv2.boundingRect(c)
            boxes.append((-cv2.contourArea(c), rect))
        boxes.sort()

        rect = boxes[0][1]
        topLeft = rect[0:2]
        bottomRight = (rect[0] + rect[2], rect[1] + rect[3])
        midpoint = ((topLeft[0] + bottomRight[0]) / 2, (topLeft[1] + bottomRight[1]) / 2)

        cv2.rectangle(thresholdImage, topLeft, bottomRight, cv.Scalar(0, 0, 255, 0))
        cv2.circle(thresholdImage, midpoint, 3, cv.Scalar(0, 255, 0, 0))

        height, width, _ = sourceImg.shape
        leftSteerThreshold = width / 3
        rightSteerTheshold = 2 * leftSteerThreshold
        cv2.line(thresholdImage, (leftSteerThreshold, 0), (leftSteerThreshold, height), cv.Scalar(255, 0, 0, 0))
        cv2.line(thresholdImage, (rightSteerTheshold, 0), (rightSteerTheshold, height), cv.Scalar(255, 0, 0, 0))

        cv2.imshow('X', thresholdImage)

        if midpoint[0] < leftSteerThreshold:
            tcpSocket.send('a')  # left
        elif midpoint[0] > rightSteerTheshold:
            tcpSocket.send('e')  # right
        else:
            tcpSocket.send(',')  # forward
finally:
    print "killing"
    tcpSocket.send(' ')  # stop
    os.system("pkill -f nxjsocketproxy")
