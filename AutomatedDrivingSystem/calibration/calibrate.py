import numpy as np
import cv2
import glob

import os

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('checkerboards/checker*')

avgMtx = np.zeros((3,3))
avgDist = np.zeros((1,5))
avgNewcameramtx = np.zeros((3,3))
avgRoi = np.zeros(4)

imCount = 0

for fname in images:
    print fname
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    checkerX = 19 # starting checkerboard size, which will decrease
    checkerY = 16 # until chessboard corners are found
    
    ret = False
    while not ret and checkerY>4:
        checkerX -= 1
        checkerY -= 1
        checkerSize = (checkerX, checkerY)
        print checkerSize

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((checkerX*checkerY,3), np.float32)
        objp[:,:2] = np.mgrid[0:checkerX,0:checkerY].T.reshape(-1,2)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, checkerSize,None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            drawnimg = cv2.drawChessboardCorners(img, checkerSize, corners2,ret)
            newfname = "corners/"+fname.split('/',1)[1]
            cv2.imwrite(newfname, drawnimg)

            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

            h,w = img.shape[:2]
            newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
            x,y,w,h = roi
            print roi

            # undistort
            dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

            if not x==y==w==h==0:#throw out results without proper roi
                avgMtx += mtx
                avgDist += dist
                avgNewcameramtx += newcameramtx
                avgRoi += np.array([x,y,w,h])
                dst = dst[y:y+h, x:x+w] #crop the image to roi
                imCount += 1
                
            newfname = "undistorted/"+fname.split('/',1)[1]
            cv2.imwrite(newfname, dst)

cv2.destroyAllWindows()

avgMtx /= imCount
avgDist /= imCount
avgNewcameramtx /= imCount
avgRoi /= imCount

print "avgMtx"
print(avgMtx)
print "avgDist"
print(avgDist)
print "avgNewcameramtx"
print(avgNewcameramtx)
print "avgRoi"
print(avgRoi)

avgMtx.dump("camera_matrix.dat")
avgDist.dump("distortion_coefficients.dat")
avgNewcameramtx.dump("refined_camera_matrix.dat")
avgRoi.astype(int).dump("region_of_interest.dat")