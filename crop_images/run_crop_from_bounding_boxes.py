import argparse
import json
import os

import cv2

import utils.crop

"""Crop images from bounding boxes annotations, optionally does augmentation"""
def parseArguments() :

    parser = argparse.ArgumentParser(description='Crop images tools for Fish dataset, bounding boxes version')

    parser.add_argument("--json_dir", type=str, required=True, help="Directory with JSON annotations")
    parser.add_argument("--src_images_dir", type=str, required=True, help="Root dir with images")
    parser.add_argument("--out_images_dir",type=str, required=True, help="Root dir for output images")
    parser.add_argument("--square_crop_size",type=int, required=True, help="Square utils size (no warping)")
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

                        crops = utils.crop.cropImageNoWarp(imageFile, heads, tails, squareSize=args.square_crop_size,
                                                augmentation=args.augmentation, debug=args.debug)

                        for index, crop in enumerate(crops) :

                            baseImageName = os.path.splitext(annotation["filename"])[0]

                            cv2.imwrite(os.path.join(args.out_images_dir,objclass,
                                                     baseImageName + "_" + str(index) + ".jpg"), crop)

                    else:

                        print ('--> WARNING: No fish in image ' + annotation["filename"] + ' of class ' + objclass)