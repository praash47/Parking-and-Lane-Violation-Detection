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
        # creating a vehicle object if it is not present in vehicles in scene
        # bounding box is updated if it is already present.
        for track in self.object.tracker.tracker.tracks:
            bbox = track.to_tlbr()
            class_name = track.get_class()
            id = track.track_id

            if id not in self.vehicles_in_scene['id']:
                vehicle_object = Vehicle(id, bbox, class_name)
                self.vehicles_in_scene['id'].append(id)
                self.vehicles_in_scene['class_name'].append(class_name)
                self.vehicles_in_scene['objects'].append(vehicle_object)
            else:
                vehicle_object = self.getVehicleById(id)
                vehicle_object.curr_bbox = bbox
                vehicle_object.prev20Bboxand10AreaAppend(bbox)
                vehicle_object.in_frame += 1
        print(self.vehicles_in_scene)


    def getVehicleById(self, id):
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
        # previous 20 bounding boxes of that vehicle and previous 10 areas of vehicles
        # that is required for other modules.
        area = abs((bbox[3]-bbox[1]) * (bbox[2]-bbox[0]))
        if len(self.prev_20_bounding_box) == 0:
            self.prev_20_bounding_box.append(bbox)
            self.prev_20_bounding_box = np.array(self.prev_20_bounding_box)
        else:
            to_append = np.array([bbox])
            self.prev_20_bounding_box = np.append(self.prev_20_bounding_box, to_append, axis=0)
            print(self.prev_20_bounding_box)
            if self.prev_20_bounding_box.shape[0] > 20:
                self.prev_20_bounding_box = np.delete(self.prev_20_bounding_box, 0, 0)
        self.prev_10_areas.append(area)
        if len(self.prev_10_areas) > 10:
            self.prev_10_areas.pop(0)
