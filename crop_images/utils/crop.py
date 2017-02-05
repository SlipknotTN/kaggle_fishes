import cv2
import numpy as np

"""Crop without any warping, optional does augmentation.
Needs heads and tails annotations."""
def cropImageNoWarp (imageFile, heads, tails, squareSize, augmentation, debug=False) :

    image = cv2.imread(imageFile)

    crops = []

    for index in range(len(heads)) :

        head = heads[index]
        tail = tails[index]
        #OpenCV 2 np array format for bounding rect
        headPoint = np.array( [[ head["x"], head["y"] ]], dtype=np.int32)
        tailPoint = np.array( [[ tail["x"], tail["y"] ]], dtype=np.int32)

        rectPoints = np.array([headPoint,tailPoint], dtype=np.int32)
        x,y,w,h = cv2.boundingRect(rectPoints)

        print x, y, w, h

        #Strict rectangle drawing
        imageDebug = np.copy(image)
        cv2.rectangle(imageDebug, pt1=tuple(headPoint[0]), pt2=tuple(tailPoint[0]), color=(0,0,255-index*50), thickness=5)

        #We need to utils a bigger shape and we need a square
        margin = 0.10

        #First of all identify max side
        portrait = False
        if (h > w) :
            portrait = True

        if portrait == False :

            newW = int(max(w + w * margin, squareSize))
            newX = int(x - (newW - w) / 2)
            newH = newW
            newY = int(y - (newH - h) / 2)

        else :

            newH = int(max(h + h * margin, squareSize))
            newY = int(y - (newH - h) / 2)
            newW = newH
            newX = int(x - (newW - w) / 2)

        limitY = newY + newH
        limitX = newX + newW

        #Adjust bounding box if exceeds the image limits
        newX = max(newX,0)
        newY = max(newY,0)
        overX = limitX - image.shape[1]
        if overX > 0:
            newX = newX - overX
        overY = limitY - image.shape[0]
        if overY > 0:
            newY = newY - overY

        cv2.rectangle(imageDebug, pt1=(newX, newY), pt2=(newX + newW, newY + newH),
                      color=(0, 255, 255 - index * 50), thickness=5)

        crop = image[newY : newY + newH, newX : newX + newW]

        if augmentation == False :
            crops.append(crop)

        else :

            #4 images rotated by 90 degrees
            center = float(crop.shape[0])/2.0, float(crop.shape[1])/2.0
            baseDegree = -90.0
            scale = 1.0
            for index in range(0,4) :
                rotMat = cv2.getRotationMatrix2D(center=center, angle=baseDegree*index, scale=scale)
                rotatedCrop = cv2.warpAffine(src=crop, M=rotMat, dsize=(crop.shape[1],crop.shape[0]))
                crops.append(rotatedCrop)

        if debug :
            cv2.imshow("default", imageDebug)
            cv2.waitKey(0)
            for finalCrop in crops:
                cv2.imshow("default", finalCrop)
                cv2.waitKey(0)

    return crops


"""Crop images for augmentation, no bounding boxes provided"""
def augmentationCropNoWarp (imageFile, squareSize, debug=False) :

    image = cv2.imread(imageFile)
    width = image.shape[1]
    height = image.shape[0]

    crops = []

    imageDebug = np.copy(image)

    #Iterate over vertical axis
    yCropIndex = 0
    while (True) :

        startY = yCropIndex * squareSize
        finishY = startY + squareSize

        #Column terminates, pick rectangle from bottom border
        if finishY >= height :
            startY = height - 1 - squareSize
            finishY = startY + squareSize

        #Crops along the row (horizontal axis)
        xCropIndex = 0
        while (True) :

            startX = xCropIndex * squareSize
            finishX = startX + squareSize

            #Row terminates, pick rectangle from right border
            if finishX >= width :

                startX = width - 1 - squareSize
                finishX = startX + squareSize

            cv2.rectangle(imageDebug, pt1=(startX, startY), pt2=(finishX, finishY),
                color=(0, 0, 255), thickness=5)

            crops.append(image[startY:finishY, startX:finishX])

            #Row terminates
            if finishX == (width - 1) :
                break

            xCropIndex += 1

        #Image terminates
        if finishY == (height - 1) :
            break

        yCropIndex += 1

    if debug:
        cv2.imshow("default", imageDebug)
        cv2.waitKey(0)
        for finalCrop in crops:
            cv2.imshow("crops", finalCrop)
            cv2.waitKey(0)

    return crops