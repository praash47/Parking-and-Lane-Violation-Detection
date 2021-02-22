"""
Responsible for keeping track of vehicles in scene and individual vehicles.
"""
# Third Party Modules ##
import numpy as np


class Vehicles:
    """
    Vehicles class is responsible for overall vehicles seen in the scene.
    """

    def __init__(self, detection_object):
        self.object = detection_object
        self.vehicles_in_scene = {
            'id': [],
            'class_name': [],
            'objects': []
        }

    def register(self):
        """
        creating a vehicle object if it is not present in vehicles in scene
        - bounding box is updated if it is already present.
        """
        # Looping in deep sort tracks
        for track in self.object.tracker.tracker.tracks:
            bbox = track.to_tlbr()
            class_name = track.get_class()
            id = track.track_id

            # If vehicle not present in scene, then create object then append in vehicles in scene.
            if id not in self.vehicles_in_scene['id']:
                vehicle_object = Vehicle(id, bbox, class_name)
                self.vehicles_in_scene['id'].append(id)
                self.vehicles_in_scene['class_name'].append(class_name)
                self.vehicles_in_scene['objects'].append(vehicle_object)
            # Else get the vehicle and update the current bounding boc
            else:
                vehicle_object = self.getVehicleById(id)
                vehicle_object.curr_bbox = bbox
                # Append the area and bbox to the record
                vehicle_object.prev20Bboxand10AreaAppend(bbox)
                # Tracking how many frames the vehicle is in.
                vehicle_object.in_frame += 1

    def getVehicleById(self, id):
        """
        To return vehicle object using id
        :param id: vehicle object to get id of
        :return: vehicle object
        """
        # Loop in Vehicles in scene.
        vehicle_object = None
        for i, obj_id in enumerate(self.vehicles_in_scene['id']):
            if id == obj_id:
                vehicle_object = self.vehicles_in_scene['objects'][i]
        return vehicle_object


class Vehicle:
    """
    A vehicle object that stores information about vehicles
    """

    def __init__(self, id, bbox, class_name):
        self.id = id
        self.curr_bbox = bbox
        self.class_name = class_name
        self.prev_20_bounding_box = []
        self.prev_10_areas = []
        self.in_frame = 1

    def prev20Bboxand10AreaAppend(self, bbox):
        """
        record of previous 20 bounding boxes of that vehicle and previous 10 areas of vehicles that is required for
        other modules.
        :param bbox: bbox to calculate area from and append.
        """
        area = abs((bbox[3] - bbox[1]) * (bbox[2] - bbox[0]))
        # If empty condition
        if len(self.prev_20_bounding_box) == 0:
            self.prev_20_bounding_box.append(bbox)
            self.prev_20_bounding_box = np.array(self.prev_20_bounding_box)
        # If already one bbox is there.
        else:
            to_append = np.array([bbox])
            # Append the bbox in previous 20 bounding boxes
            self.prev_20_bounding_box = np.append(self.prev_20_bounding_box, to_append, axis=0)
            # If more than 20, delete the first record.
            if self.prev_20_bounding_box.shape[0] > 20:
                self.prev_20_bounding_box = np.delete(self.prev_20_bounding_box, 0, 0)

        if len(self.prev_10_areas) <= 4:
            self.prev_10_areas.append(area)
        else:
            temp_numpy_array = np.array(self.prev_10_areas)
            length = len(self.prev_10_areas)
            q1 = np.median(temp_numpy_array[:int(length/2)])
            q3 = np.median(temp_numpy_array[int(length/2):])
            qd = 0.5 * (q3 - q1)
            if area > q3:
                upper_outlier_threshold = q3 + 3 * qd
                if area < upper_outlier_threshold:
                    self.prev_10_areas.append(area)
            elif area < q1:
                lower_outlier_threshold = q1 - 3 * qd
                if area > lower_outlier_threshold:
                    self.prev_10_areas.append(area)
        # If more than 10 areas, then remove the first one area.
        if len(self.prev_10_areas) > 10:
            self.prev_10_areas.pop(0)
