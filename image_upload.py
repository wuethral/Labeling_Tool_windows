from tkinter import *
from PIL import Image, ImageTk
import cv2
import os


def uploading_images():


    vidcap = cv2.VideoCapture('Example.mp4')
    success, image = vidcap.read()
    count = 0
    success = True
    while success:
        success, image = vidcap.read()
        if image is not None:
            name = 'frame' + str(count) + '.jpg'
            cv2.imwrite(name, image)  # save frame as JPEG file
            count += 1


      #  if cv2.waitKey(10) == 27:  # exit if Escape is hit
      #      break
    return count