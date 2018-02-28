import cv2
import numpy as np

from matplotlib import pyplot as plt #remove me!

def undistort(image):
    mtx = np.load("calibration/camera_matrix.dat")
    dist = np.load("calibration/distortion_coefficients.dat")
    newcameramtx = np.load("calibration/refined_camera_matrix.dat")
    roi = tuple(np.load("calibration/region_of_interest.dat"))
    undistorted = cv2.undistort(image, mtx, dist, None, newcameramtx)
    
    x,y,w,h = roi
    undistorted = undistorted[y:y+h, x:x+w]
    
    return undistorted

def birdsEyeTransform(image, direction):
    work = image
    
    # perspective trapezoid for road ahead
    bottomWidth = 1.0
    topWidth = 0.28
    trapHeight = 0.35
    
    imgHeight, imgWidth = work.shape[:2]
    
    srcPoints = np.zeros((4, 2), dtype = "float32")
    srcPoints[0] = [ (imgWidth*(0.5-topWidth/2)), (imgHeight*(1-trapHeight)) ] #top left
    srcPoints[1] = [ (imgWidth*(0.5+topWidth/2)), (imgHeight*(1-trapHeight)) ] #top right
    srcPoints[2] = [ (imgWidth*(0.5+bottomWidth/2)), (imgHeight) ] #bottom right
    srcPoints[3] = [ (imgWidth*(0.5-bottomWidth/2)), (imgHeight) ] #bottom left
    
    dstPoints = np.zeros((4, 2), dtype = "float32")
    dstPoints[0] = [ (imgWidth*(0.5-bottomWidth/2)), (0) ] #top left
    dstPoints[1] = [ (imgWidth*(0.5+bottomWidth/2)), (0) ] #top right
    dstPoints[2] = [ (imgWidth*(0.5+bottomWidth/2)), (imgHeight) ] #bottom right
    dstPoints[3] = [ (imgWidth*(0.5-bottomWidth/2)), (imgHeight) ] #bottom left
    
    transformMatrix = cv2.getPerspectiveTransform(srcPoints,dstPoints) if (direction==0) else cv2.getPerspectiveTransform(dstPoints,srcPoints)
    
    outputSize = (dstPoints[2][0], dstPoints[2][1])
    work = cv2.warpPerspective(work, transformMatrix, outputSize, flags=cv2.INTER_LINEAR)
    
    return work


def detectLanes(image):
    work = image
    work = birdsEyeTransform(work, 0)
    work = birdsEyeTransform(work, 1)
    return work


# old lane detection

def movingaverage (values, window):
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'valid')
    return sma

def detectLanesOld(image):
    original = image
    cv2.imwrite('1.png', original)
    work = undistort(image)
    work = image #remove me!
    
    # perspective trapezoid for road ahead
    bottomWidth = 1.0
    topWidth = 0.28
    trapHeight = 0.35
    
    imgHeight, imgWidth = work.shape[:2]
    
    srcPoints = np.zeros((4, 2), dtype = "float32")
    srcPoints[0] = [ (imgWidth*(0.5-topWidth/2)), (imgHeight*(1-trapHeight)) ] #top left
    srcPoints[1] = [ (imgWidth*(0.5+topWidth/2)), (imgHeight*(1-trapHeight)) ] #top right
    srcPoints[2] = [ (imgWidth*(0.5+bottomWidth/2)), (imgHeight) ] #bottom right
    srcPoints[3] = [ (imgWidth*(0.5-bottomWidth/2)), (imgHeight) ] #bottom left
    
    dstPoints = np.zeros((4, 2), dtype = "float32")
    dstPoints[0] = [ (imgWidth*(0.5-bottomWidth/2)), (0) ] #top left
    dstPoints[1] = [ (imgWidth*(0.5+bottomWidth/2)), (0) ] #top right
    dstPoints[2] = [ (imgWidth*(0.5+bottomWidth/2)), (imgHeight) ] #bottom right
    dstPoints[3] = [ (imgWidth*(0.5-bottomWidth/2)), (imgHeight) ] #bottom left
    
    transformMatrix = cv2.getPerspectiveTransform(srcPoints,dstPoints)
    
    outputSize = (dstPoints[2][0], dstPoints[2][1])
    work = cv2.warpPerspective(work, transformMatrix, outputSize, flags=cv2.INTER_LINEAR)
    
    cv2.imwrite('2.png', work)
    
    imgColor = work
    work = cv2.cvtColor(work,cv2.COLOR_BGR2GRAY)
    
    work = cv2.Sobel(work,cv2.CV_64F,1,0,ksize=5)
    work = np.absolute(work)
    work = np.uint8(work)
    
    cv2.imwrite('3.png', work)
    
    lastLeftLanePoint = (0,0)
    lastRightLanePoint = (0,0)
    
    verticalBins = 5
    movingAvgWindow = int(round(0.08*work.shape[1]))
    for vBin in range(verticalBins):
        yMin = (work.shape[0]/verticalBins)*vBin
        yMax = (work.shape[0]/verticalBins)*(vBin+1)
        results = []
        for col in range(work.shape[1]):
            results.append(sum(work[yMin:yMax,col])/work.shape[0])

        avgresults = movingaverage(results,movingAvgWindow)
        avgresults = np.insert(avgresults,0,np.zeros(int(movingAvgWindow/2)))

        leftLanePos = avgresults[0:len(avgresults)/2].argmax()
        rightLanePos = avgresults[len(avgresults)/2:].argmax() + len(avgresults)/2

        yPos = (yMin+yMax)/2
        color = (0,0,255)

        curLeftLanePoint = (leftLanePos,yPos)
        curRightLanePoint = (rightLanePos,yPos)
    
        if lastLeftLanePoint!=(0,0):
            imgColor = cv2.line(imgColor, lastLeftLanePoint, curLeftLanePoint, color, 15, cv2.LINE_AA)
            imgColor = cv2.line(imgColor, lastRightLanePoint, curRightLanePoint, color, 15, cv2.LINE_AA)
            
        lastLeftLanePoint = curLeftLanePoint
        lastRightLanePoint = curRightLanePoint

        if vBin==4:
            plt.plot(range(len(results)),results,range(len(avgresults)),avgresults)
            plt.show()
    
    work = imgColor
    
    cv2.imwrite('4.png', work)
    
    transformMatrix = cv2.getPerspectiveTransform(dstPoints,srcPoints)
    
    outputSize = (srcPoints[2][0], srcPoints[2][1])
    work = cv2.warpPerspective(work, transformMatrix, outputSize, flags=cv2.INTER_LINEAR)
    
    cv2.imwrite('5.png', work)
    
    return work