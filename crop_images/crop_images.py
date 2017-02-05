import argparse
import json

import os
import cv2

import numpy as np

"""Crop without any warping"""
def cropImage (imageFile, heads, tails, squareSize, augmentation, debug=False) :

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

        #We need to crop a bigger shape and we need a square
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

def parseArguments() :

    parser = argparse.ArgumentParser(description='Crop images tools for Fish dataset')

    parser.add_argument("--json_dir", type=str, required=True, help="Directory with JSON annotations")
    parser.add_argument("--src_images_dir", type=str, required=True, help="Root dir with images")
    parser.add_argument("--out_images_dir",type=str, required=True, help="Root dir for output images")
    parser.add_argument("--square_crop_size",type=int, required=True, help="Square crop size (no warping)")
    parser.add_argument("--augmentation", action="store_true",help="Enable Augmentation")
    parser.add_argument("--debug", action="store_true",help="Enable Debug")

    return parser

if __name__ == '__main__':

    parser = parseArguments()
    args = parser.parse_args()

    objclasses = ['ALB','BET','DOL','LAG','OTHER','SHARK','YFT']

    for objclass in objclasses :

        print(objclass)

        srcImagesDir = os.path.join(args.src_images_dir, objclass)
        jsonDir = os.path.join(args.json_dir, objclass)

        if os.path.exists(srcImagesDir) and os.path.exists(jsonDir) :

            #Read JSON
            jsonFile = os.path.join(jsonDir,objclass.lower() + '_labels.json')
            with open(jsonFile, 'r') as jsonAnnotationsFile :
                annotations = json.load(jsonAnnotationsFile)
                for annotation in annotations:
                    print(annotation)

                    if (len(annotation["annotations"]) % 2) != 0 :
                        raise Exception ('Error in length of the annotation for ' + annotation["filename"] + ' of class ' + objclass)

                    if len(annotation["annotations"]) > 0:

                        if len(annotation["annotations"]) > 2:
                            print ('--> WARNING: More than one fish in image ' + annotation["filename"] + ' of class ' + objclass)

                        heads = []
                        tails = []

                        for index in range(len(annotation["annotations"])/2) :

                            heads.append(annotation["annotations"][index*2])
                            tails.append(annotation["annotations"][index*2 + 1])

                        imageFile = os.path.join(srcImagesDir, annotation["filename"])

                        if (os.path.exists(imageFile) == False) :
                            raise Exception ("Image not found: " + imageFile)

                        crops = cropImage(imageFile, heads, tails, squareSize=args.square_crop_size,
                                          augmentation=args.augmentation, debug=args.debug)

                        for index, crop in enumerate(crops) :

                            baseImageName = os.path.splitext(annotation["filename"])[0]

                            cv2.imwrite(os.path.join(args.out_images_dir,objclass,
                                                     baseImageName + "_" + str(index) + ".jpg"), crop)

                    else:

                        print ('--> WARNING: No fish in image ' + annotation["filename"] + ' of class ' + objclass)