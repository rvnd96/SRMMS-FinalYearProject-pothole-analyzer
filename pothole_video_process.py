import json
import cv2
from PIL import Image
from tqdm import tqdm
import numpy as np
from numpyencoder import NumpyEncoder

import pothole

video_file = "sample_small_video.mp4"
json_output_file = "video_potholes.json"
temporary_image_file_name = "video_snaphot.jpg"

video_reader = cv2.VideoCapture(video_file)
nb_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
frame_h = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_w = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))

potholes = []

for i in tqdm(range(nb_frames)):
    print("Frame {}/{}".format(i,nb_frames))
    _, image = video_reader.read()
    
    pil_image = Image.fromarray(np.uint8(image))

    rgb_im = pil_image.convert('RGB')
    rgb_im.save(temporary_image_file_name)

    frame_detected = pothole.detect_and_color_splash(temporary_image_file_name)
    potholes.append({
        'frame': i,
        'data': frame_detected
    })

video_reader.release()

json_str = json.dumps(potholes, cls=NumpyEncoder, indent=4)
with open(json_output_file, "w") as text_file:
    text_file.write(json_str)

print("Check \"{}\"".format(json_output_file))