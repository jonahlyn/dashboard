#!/usr/bin/env python3

import logging
logging.getLogger('tensorflow').disabled = True

import os
from pathlib import Path
import subprocess as sp
import datetime as dt
import time as tm
import cv2
import numpy as np
import mrcnn.config
import mrcnn.utils
from mrcnn.model import MaskRCNN
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'appdb'
TABLES = {}
TABLES['data'] = (
    "CREATE TABLE `data` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `date` datetime NOT NULL,"
    "  `vehicles` smallint NOT NULL,"
    "  `filename` varchar(512) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")


FFMPEG_BIN = '/usr/bin/ffmpeg'
RTSP_STREAM = "https://590804fbbbc47.streamlock.net:444/ruidosowebcorp2/ruidosowebcorp2.stream/playlist.m3u8"

COMMAND = [ FFMPEG_BIN,
            '-loglevel', 'panic',
            '-i', RTSP_STREAM,
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-']

VWIDTH = 800
VHEIGHT = 450


class MaskRCNNConfig(mrcnn.config.Config):
    """ Mask-RCNN Configuration"""

    NAME = "coco_pretrained_model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 1 + 80  # COCO dataset has 80 classes + one background class
    DETECTION_MIN_CONFIDENCE = 0.6


def get_car_boxes(boxes, class_ids):
  '''
  Filter a list of Mask R-CNN detection results to get only the detected cars / trucks
  '''

  car_boxes = []
  for i, box in enumerate(boxes):
      # If the detected object isn't a car/bus/truck, skip it
      if class_ids[i] in [3, 8, 6]:
          car_boxes.append(box)

  return np.array(car_boxes)


# Download the pretrained weights
CURRENT_DIR = Path(".")
MODEL_DIR = os.path.join(CURRENT_DIR, "logs")
MODEL_PATH = os.path.join(CURRENT_DIR, "mask.rcnn.coco.h5")

if not os.path.exists(MODEL_PATH):
  mrcnn.utils.download_trained_weights(MODEL_PATH)

# Create the model to be used for object detection
model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=MaskRCNNConfig())
model.load_weights(MODEL_PATH, by_name=True)

# Grab an image from the RTSP stream
pipe = sp.Popen(COMMAND, stdin = sp.PIPE, stdout = sp.PIPE)
raw_image = pipe.stdout.read(VWIDTH*VHEIGHT*3) # = 1 frame
image =  np.frombuffer(raw_image, dtype='uint8').reshape((VHEIGHT,VWIDTH,3))

image_copy = image.copy()

# Detect vehicles and draw bounding boxes
results = model.detect([image_copy], verbose=0)
result = results[0]
car_boxes = get_car_boxes(result['rois'], result['class_ids'])

for box in car_boxes:
  y1, x1, y2, x2 = box
  cv2.rectangle(image_copy, (x1, y1), (x2, y2), (0,255,0), 2)

# Save file to disk
d = dt.datetime.fromtimestamp(tm.time())
output_img = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR)
file_name = "output_{}.png".format(d.strftime('%Y%m%d%H%M%S'))
cv2.imwrite("data/{}".format(file_name), output_img)

output_data = (d, len(car_boxes), file_name)


# Get a connection to the database
try:
    cnx = mysql.connector.connect(user='appuser', password='apppassword',
                                  host='127.0.0.1',
                                  database='appdb')
    cursor = cnx.cursor()

    # Create database table if necessary
    for table_name in TABLES:
        try:
            print("Creating table {}\n".format(table_name), end='')
            cursor.execute(TABLES[table_name])
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.\n")
            else:
                print(err.msg)

    # Write results to database
    print("Writing database record\n")
    add_record = ("INSERT INTO data "
                    "(date, vehicles, filename) "
                    "VALUES (%s, %s, %s)")
    cursor.execute(add_record, output_data)
    cnx.commit()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("User name or password was incorrect\n")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist\n")
    else:
        print(err)
finally:
    print("Closing database connection")
    if(cnx is not None):
        cnx.close()
