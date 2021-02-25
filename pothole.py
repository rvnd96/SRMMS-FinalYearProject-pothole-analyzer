from mrcnn import model as modellib, utils
from mrcnn.config import Config

import os
import sys
import json
import datetime
import numpy as np
import skimage.draw
import cv2
from mrcnn.visualize import display_instances
import matplotlib.pyplot as plt
from numpyencoder import NumpyEncoder
from keras.backend import clear_session

rng = np.random

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")

class CustomConfig(Config):
    NAME = "damage"
    IMAGES_PER_GPU = 3
    NUM_CLASSES = 1 + 1  # Background + 1 Pothole
    STEPS_PER_EPOCH = 1000
    VALIDATION_STEPS = 50
    # Skip detections with < 90% confidence
    # DETECTION_MIN_CONFIDENCE = 0.9
    # IMAGE_MAX_DIM=800
    # IMAGE_MIN_DIM=800

def color_splash(image, mask):
    """Apply color splash effect.
    image: RGB image [height, width, 3]
    mask: instance segmentation mask [height, width, instance count]

    Returns result image.
    """
    # Make a grayscale copy of the image. The grayscale copy still
    # has 3 RGB channels, though.
    gray = skimage.color.gray2rgb(skimage.color.rgb2gray(image)) * 255
    # We're treating all instances as one, so collapse the mask into one layer
    mask = (np.sum(mask, -1, keepdims=True) >= 1)
    # Copy color pixels from the original color image where mask is set
    if mask.shape[0] > 0:
        splash = np.where(mask, image, gray).astype(np.uint8)
    else:
        splash = gray
    return splash

# weights file to load
weights_path = "mask_rcnn_damage_0160.h5"
print("Weights: ", weights_path)
print("Logs: ", DEFAULT_LOGS_DIR)

# Configurations
class InferenceConfig(CustomConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
config = InferenceConfig()
config.display()

# Create model
global model
model = modellib.MaskRCNN(mode="inference", config=config,  model_dir=DEFAULT_LOGS_DIR)


# Load weights
print("Loading weights ", weights_path)
model.load_weights(weights_path, by_name=True)
model.keras_model._make_predict_function()


def detect_and_color_splash(image_path=None):
    global model
    #print(model)
    assert image_path

    # Run model detection and generate the color splash effect
    print("Running on {}".format(image_path))
    # Read image
    image = skimage.io.imread(image_path)
    # Remove alpha channel, if it has one
    #if image.shape[-1] == 4:
    #    image = image[..., :3]
    # Detect objects
    r = model.detect([image], verbose=1)[0]
    
    # Color splash
    splash = color_splash(image, r['masks'])

    for i in range(len(r['rois'])):
        color = (57, 255, 20)
        # get coordinates
        y1, x1, y2, x2 = r['rois'][i]
        # calculate width and height of the box
        width, height = x2 - x1, y2 - y1
        cv2.rectangle(splash, (x1,y1), (x2,y2), color, 2)
        cv2.putText(splash, str(i+1), (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    #with open('data.json', 'w') as outfile:
    #    json.dump(r, outfile, cls=NumpyEncoder)
    
    # Save output

    # file_name = "splash2_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
    # skimage.io.imsave(file_name, image)

    file_name = "current_masked.jpg"
    skimage.io.imsave(file_name, splash)
    #print("Saved to ", file_name)

    del r['masks']

    return r

if __name__ == '__main__':
    detect_and_color_splash('current.jpg')