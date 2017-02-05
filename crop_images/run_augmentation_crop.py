import argparse
import json
import os

import cv2

import utils.crop

"""Crop images for data augmentation, no bounding boxes provided"""
def parseArguments() :

    parser = argparse.ArgumentParser(description='Crop images tools for data augmentation')

    parser.add_argument("--src_images_dir", type=str, required=True, help="Root dir with images")
    parser.add_argument("--out_images_dir",type=str, required=True, help="Root dir for output images")
    parser.add_argument("--square_crop_size",type=int, required=True, help="Square utils size (no warping)")
    parser.add_argument("--debug", action="store_true",help="Enable Debug")

    return parser

if __name__ == '__main__':

    parser = parseArguments()
    args = parser.parse_args()

    objclasses = ['NoF']

    for objclass in objclasses :

        print(objclass)

        srcImagesDir = os.path.join(args.src_images_dir, objclass)

        if os.path.exists(srcImagesDir):

            #Get images files
            imageFiles = [os.path.join(srcImagesDir, f) for f in os.listdir(srcImagesDir) if os.path.isfile(os.path.join(srcImagesDir, f))]

            for imageFile in imageFiles :

                print ("Cropping image: " + imageFile)

                crops = utils.crop.augmentationCropNoWarp(imageFile, squareSize=args.square_crop_size,
                                                debug=args.debug)

                for index, crop in enumerate(crops) :

                    baseImageName = os.path.splitext(os.path.basename(imageFile))[0]

                    cv2.imwrite(os.path.join(args.out_images_dir,objclass,
                                                     baseImageName + "_" + str(index) + ".jpg"), crop)