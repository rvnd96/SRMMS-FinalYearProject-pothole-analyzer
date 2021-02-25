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


def detect_and_color_splash(model, image_path=None):
    assert image_path

    # Run model detection and generate the color splash effect
    print("Running on {}".format(args.image))
    # Read image
    image = skimage.io.imread(args.image)
    # Detect objects
    r = model.detect([image], verbose=1)[0]
    print(r['rois'])

    # for box in r['rois']:
    #     color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
    #     # get coordinates
    #     y1, x1, y2, x2 = box
    #     # calculate width and height of the box
    #     width, height = x2 - x1, y2 - y1
    #     cv2.rectangle(image, (x1,y1), (x2,y2), color, 2)

    #with open('data.json', 'w') as outfile:
    #    json.dump(r, outfile, cls=NumpyEncoder)
    # Color splash
    splash = color_splash(image, r['masks'])
    # Save output

    # file_name = "splash2_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
    # skimage.io.imsave(file_name, image)

    file_name = "splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
    skimage.io.imsave(file_name, splash)
    print("Saved to ", file_name)

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Train Mask R-CNN to detect custom class.')
    parser.add_argument("command",
                        metavar="<command>",
                        help="'train' or 'splash'")
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/custom/dataset/",
                        help='Directory of the custom dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--image', required=False,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--video', required=False,
                        metavar="path or URL to video",
                        help='Video to apply the color splash effect on')
    args = parser.parse_args()

    # Validate arguments
    if args.command == "train":
        assert args.dataset, "Argument --dataset is required for training"
    elif args.command == "splash":
        assert args.image or args.video,\
            "Provide --image or --video to apply color splash"

    print("Weights: ", args.weights)
    print("Dataset: ", args.dataset)
    print("Logs: ", args.logs)

    # Configurations
    class InferenceConfig(CustomConfig):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
    config = InferenceConfig()
    config.display()

    # Create model
    model = modellib.MaskRCNN(mode="inference", config=config,
                                  model_dir=args.logs)

    # weights file to load
    weights_path = args.weights

    # Load weights
    print("Loading weights ", weights_path)
    if args.weights.lower() == "coco":
        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])
    else:
        model.load_weights(weights_path, by_name=True)

    # evaluate
    detect_and_color_splash(model, image_path=args.image)
