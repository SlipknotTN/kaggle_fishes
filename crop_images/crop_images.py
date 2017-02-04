import argparse
import json

import os
import cv2

import numpy as np

def cropImage (imageFile, head, tail, debug=False) :

    image = cv2.imread(imageFile)

    headPoint = np.array([head["x"],head["y"]], dtype=np.int32)
    tailPoint = np.array([tail["x"],tail["y"]], dtype=np.int32)

    cv2.rectangle(image, pt1=tuple(headPoint), pt2=tuple(tailPoint), color=(0,0,255), thickness=5)

    cv2.imshow("default", image)
    cv2.waitKey(0)

    pass

def parseArguments() :

    parser = argparse.ArgumentParser(description='Crop images tools for Fish dataset')

    parser.add_argument(
        "--json_dir",
        type=str, required=True,
        help="Directory with JSON annotations"
    )

    parser.add_argument(
        "--src_images_dir",
        type=str, required=True,
        help="Root dir with images"
    )

    parser.add_argument(
        "--out_images_dir",
        type=str, required=True,
        help="Root dir for output images"
    )

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
                    if len(annotation["annotations"]) > 0:
                        head = annotation["annotations"][0]
                        tail = annotation["annotations"][1]

                        imageFile = os.path.join(srcImagesDir, annotation["filename"])

                        if (os.path.exists(imageFile) == False) :
                            raise Exception ("Image not found: " + imageFile)

                        cropImage(imageFile, head, tail, debug=True)

                        if len(annotation["annotations"]) > 2:
                            print ('--> WARNING: More than one fish in image ' + annotation["filename"] + ' of class ' + objclass)
                    else:
                        print ('--> WARNING: No fish in image ' + annotation["filename"] + ' of class ' + objclass)