import os

# comment out below line to enable tensorflow logging outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import time
import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from absl import app, flags, logging
from absl.flags import FLAGS
import yolo.core.utils as utils
from yolo.core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from yolo.core.config import cfg
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
# deep sort imports
from yolo.deep_sort import preprocessing, nn_matching
from yolo.deep_sort.detection import Detection
from yolo.deep_sort.tracker import Tracker
from yolo.tools import generate_detections as gdet
from misc.settings import *


class DetectorTracker:
    def __init__(self, detection_object):
        self.flags = {
            'tiny': False,
            'model': lane_yolo_model_to_use,
            'size': 416,
            'framework': 'tf',
            'weights': 'yolo/checkpoints/yolov4-416',
            'iou': 0.45,
            'score': 0.50,
        }
        self.detection_object = detection_object
        # Definition of the parameters
        self.max_cosine_distance = 0.4
        self.nn_budget = None
        self.nms_max_overlap = 1.0

        # initialize deep sort
        self.model_filename = 'yolo/model_data/mars-small128.pb'
        self.encoder = gdet.create_box_encoder(self.model_filename, batch_size=1)
        # calculate cosine distance metric
        self.metric = nn_matching.NearestNeighborDistanceMetric("cosine", self.max_cosine_distance, self.nn_budget)
        # initialize tracker
        self.tracker = Tracker(self.metric)

        # load configuration for object detector
        self.config = ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.session = InteractiveSession(config=self.config)
        STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(self.flags)
        self.input_size = self.flags['size']

        # load tflite model if flag is set
        if self.flags['framework'] == 'tflite':
            self.interpreter = tf.lite.Interpreter(model_path=self.flags['weights'])
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            print(self.input_details)
            print(self.output_details)
        # otherwise load standard tensorflow saved model
        else:
            self.saved_model_loaded = tf.saved_model.load(self.flags['weights'], tags=[tag_constants.SERVING])
            self.infer = self.saved_model_loaded.signatures['serving_default']
        self.frame_num = 0
        self.frame = None
        self.frame_size = None
        self.image_data = None
        self.pred = None
        self.batch_data = None
        self.pred_bbox = None
        self.boxes = None
        self.pred_conf = None
        self.scores = None
        self.classes = None
        self.valid_detections = None
        self.num_objects = None
        self.bboxes = None
        self.original_h = None
        self.original_w = None
        self.class_names = None
        self.allowed_classes = None
        self.names = []
        self.deleted_indx = []
        self.class_indx = None
        self.class_name = None
        self.object_track_count = None
        self.features = None
        self.detections = None
        self.cmap = None
        self.colors = None
        self.boxs = None
        self.indices = None
        self.start_time = None
        self.fps = None
        self.video_path = self.detection_object.video.path

    def yoloDetect(self):
        if self.detection_object.frame is not None:
            self.detection_object.roi.frame = cv2.cvtColor(self.detection_object.roi.frame, cv2.COLOR_BGR2RGB)
            # image = Image.fromarray(self.detection_object.frame)  # Tkinter readable image
            self.frame_num += 1
            print('Frame #: ', self.frame_num)
            self.frame_size = self.detection_object.frame.shape[:2]
            self.image_data = cv2.resize(self.detection_object.roi.frame, (self.input_size, self.input_size))
            self.image_data = self.image_data / 255.
            self.image_data = self.image_data[np.newaxis, ...].astype(np.float32)
            self.start_time = time.time()

            # run detections on tflite if flag is set
            if self.flags['framework'] == 'tflite':
                self.interpreter.set_tensor(self.input_details[0]['index'], self.image_data)
                self.interpreter.invoke()
                self.pred = [self.interpreter.get_tensor(self.output_details[i]['index']) for i in range(len(
                    self.output_details))]
                # run detections using yolov3 if flag is set
                if self.flags['model'] == 'yolov3' and self.flags['tiny'] == True:
                    self.boxes, self.pred_conf = filter_boxes(self.pred[1], self.pred[0], score_threshold=0.25,
                                                              input_shape=tf.constant([self.input_size, self.input_size]))
                else:
                    self.boxes, self.pred_conf = filter_boxes(self.pred[0], self.pred[1], score_threshold=0.25,
                                                              input_shape=tf.constant([self.input_size, self.input_size]))

            else:
                self.batch_data = tf.constant(self.image_data)
                self.pred_bbox = self.infer(self.batch_data)
                for key, value in self.pred_bbox.items():
                    self.boxes = value[:, :, 0:4]
                    self.pred_conf = value[:, :, 4:]

            self.boxes, self.scores, self.classes, self.valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(self.boxes, (tf.shape(self.boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    self.pred_conf, (tf.shape(self.pred_conf)[0], -1, tf.shape(self.pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=self.flags['iou'],
                score_threshold=self.flags['score']
            )

            # convert data to numpy arrays and slice out unused elements
            self.num_objects = self.valid_detections.numpy()[0]
            self.bboxes = self.boxes.numpy()[0]
            self.bboxes = self.bboxes[0:int(self.num_objects)]
            self.scores = self.scores.numpy()[0]
            self.scores = self.scores[0:int(self.num_objects)]
            self.classes = self.classes.numpy()[0]
            self.classes = self.classes[0:int(self.num_objects)]

            # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, width, height
            self.original_h, self.original_w, _ = self.detection_object.frame.shape
            self.bboxes = utils.format_boxes(self.bboxes, self.original_h, self.original_w)

            # store all predictions in one parameter for simplicity when calling functions
            self.pred_bbox = [self.bboxes, self.scores, self.classes, self.num_objects]

            # read in all class names from config
            self.class_names = utils.read_class_names(cfg.YOLO.CLASSES)

            # by default allow all classes in .names file
            #self.allowed_classes = list(self.class_names.values())

            # custom allowed classes (uncomment line below to customize tracker for only people)
            self.allowed_classes = ['car', 'truck', 'motorbike', 'bus']

            # loop through objects and use class index to get class name, allow only classes in allowed_classes list
            names = []
            for i in range(self.num_objects):
                self.class_indx = int(self.classes[i])
                self.class_name = self.class_names[self.class_indx]
                if self.class_name not in self.allowed_classes:
                    self.deleted_indx.append(i)
                else:
                    names.append(self.class_name)
            names = np.array(names)
            self.object_track_count = len(names)
            # delete detections that are not in allowed_classes
            self.bboxes = np.delete(self.bboxes, self.deleted_indx, axis=0)
            self.scores = np.delete(self.scores, self.deleted_indx, axis=0)

            # encode yolo detections and feed to tracker
            self.features = self.encoder(self.detection_object.frame, self.bboxes)
            self.detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in
                          zip(self.bboxes, self.scores, names, self.features)]

            # initialize color map
            self.cmap = plt.get_cmap('tab20b')
            self.colors = [self.cmap(i)[:3] for i in np.linspace(0, 1, 20)]

            # run non-maxima supression
            self.boxs = np.array([d.tlwh for d in self.detections])
            self.scores = np.array([d.confidence for d in self.detections])
            self.classes = np.array([d.class_name for d in self.detections])
            self.indices = preprocessing.non_max_suppression(self.boxs, self.classes, self.nms_max_overlap, self.scores)
            self.detections = [self.detections[i] for i in self.indices]

    def deepSortTrack(self):
        # Call the tracker
        self.tracker.predict()
        self.tracker.update(self.detections)

        # update tracks
        for track in self.tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            bbox = track.to_tlbr()
            class_name = track.get_class()

            # draw bbox on screen
            color = self.colors[int(track.track_id) % len(self.colors)]
            color = [i * 255 for i in color]
            cv2.rectangle(self.detection_object.roi.frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
            cv2.rectangle(self.detection_object.roi.frame, (int(bbox[0]), int(bbox[1] - 30)),
                          (int(bbox[0]) + (len(class_name) + len(str(track.track_id))) * 17, int(bbox[1])), color, -1)
            cv2.putText(self.detection_object.roi.frame, class_name + "-" + str(track.track_id), (int(bbox[0]), int(bbox[1] - 10)), 0, 0.75,
                        (255, 255, 255), 2)

        # calculate frames per second of running detections
        self.fps = 1.0 / (time.time() - self.start_time)
        print("FPS: %.2f" % self.fps)
        self.detection_object.roi.frame = np.asarray(self.detection_object.roi.frame)
        self.detection_object.roi.frame = cv2.cvtColor(self.detection_object.roi.frame, cv2.COLOR_RGB2BGR)
