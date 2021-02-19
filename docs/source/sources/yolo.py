"""
YOLOv3 module for parking violation
"""
# Local Modules ##
from misc.settings import *


# noinspection PyTypeChecker
class YOLO:
    def __init__(self, detection_object):
        """
        Load YOLO weights.
        :param detection_object: parking violation object
        """
        self.object = detection_object
        self.disabled = False  # used to disable YOLO from functioning.

        self.outputs = ''
        self.bounding_box = []
        self.classes = []
        self.class_names = []

        # Read classes from the file and place in the classes list.
        with open(parking_yolo_coco_names, "r") as names_file:
            self.classes = [line.strip() for line in names_file.readlines()]

        # OpenCV's direct YOLO v3 reading Deep Neural Network Module
        # Load the yolo weights and use Deep Neural Network to realize it.
        self.net = cv2.dnn.readNet(parking_yolo_config, parking_yolo_weights)

        # Saying that OpenCV with handle YOLO
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

        # We want to run YOLO on our CPU
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detector(self):
        """
        a shorthand function for full YOLO execution
        """

        # If there is a frame and yolo is not disabled, start YOLO detections.
        if self.object.roi.frame is not None and not self.disabled:
            self.findObjects()
            self.placeObjects()

    def findObjects(self):
        """
        Main function where YOLO carries out its detections and classifications

        At the end: :outputs gets the objects in the frame
        """
        # A blob is generated from the image using Dark Neural Network Module
        blob = cv2.dnn.blobFromImage(self.object.roi.frame, parking_yolo_dnn_blob_scale_factor,
                                     (parking_yolo_dnn_blob_output_size, parking_yolo_dnn_blob_output_size),
                                     parking_yolo_dnn_blob_mean_sub_value, parking_yolo_dnn_blob_swap_RB,
                                     crop=parking_yolo_dnn_blob_crop)
        # We set the blob as input to the neural network
        self.net.setInput(blob)

        # Get layer names list inside the loaded weights
        layer_names = self.net.getLayerNames()

        # Get output names from the neural network using the layers
        # uses list comprehension
        output_names = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        # Send the output names to the neural networks
        self.outputs = self.net.forward(output_names)

    def placeObjects(self):
        """
        from the yolo outputs, get the indices and it's corresponding detection properties.
        """
        bounding_boxes = []
        class_ids = []
        confidences = []

        for output in self.outputs:  # Outputs is a list of output
            for det in output:  # Output is a list of multiple detections
                scores = det[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # If confidence is higher than our set confidence, then only regard the detection
                if confidence > parking_yolo_confidence_threshold:
                    # Computation of width of that object and it's origin
                    height, width, channels = self.object.roi.frame.shape
                    width_det_object, height_det_object = int(det[2] * width), int(det[3] * height)
                    origin_x_det_object, origin_y_det_object = int((det[0] * width) - width_det_object / 2), int(
                        (det[1] *
                         height) - height_det_object / 2)
                    # Append into the arrays
                    bounding_boxes.append(
                        [origin_x_det_object, origin_y_det_object, width_det_object, height_det_object])
                    class_ids.append(class_id)
                    confidences.append(float(confidence))

        # Get indices out so that it is used for drawing the bounding boxes.
        # It applies Non-max suppression and gets the bounding boxes with highest objectiveness score
        # - Removes false bounding boxes
        # - Without this, many bounding boxes will appear around the detections.
        indices = cv2.dnn.NMSBoxes(bounding_boxes, confidences, parking_yolo_confidence_threshold,
                                   parking_yolo_nms_threshold)

        # Draw bounding box for each detection
        for index in indices:
            index = index[0]
            self.drawBoundingBox(index, class_ids, confidences, bounding_boxes)

    def drawBoundingBox(self, index, class_ids, confidences, bounding_boxes):
        """
        draws bounding box on the screen.

        :param index: Index of which bounding box to draw
        :param class_ids: the class ids list
        :param confidences: the confidences list
        :param bounding_boxes: the bounding_boxes list
        """
        bounding_box = bounding_boxes[index]
        x, y, w, h = bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3]
        self.bounding_box.append([x, y, w, h])

        cv2.rectangle(self.object.roi.frame, (x, y), (x + w, y + h), parking_yolo_bbox_color,
                      parking_yolo_bbox_thickness)
        cv2.putText(self.object.roi.frame, f'{self.classes[class_ids[index]].upper()} {int(confidences[index] * 100)}%',
                    (x, y - 10), parking_yolo_bbox_font, parking_yolo_bbox_font_scale, parking_yolo_bbox_color,
                    parking_yolo_bbox_thickness)
        # Our local variable class_names to track what classes are present in the detections.
        self.class_names.append(self.classes[class_ids[index]])

    def disable(self):
        self.disabled = True
        self.object.option_menu.add_command(label="Enable YOLO", command=self.enable)

    def enable(self):
        self.disabled = False
        self.object.option_menu.add_command(label="Disable YOLO", command=self.disable)
