# Parking and Lane Violation Detection
 Parking and Lane Violation Detection using Object Detector and Tracker

## Setup Step by Step
### Yolo and Tracker
#### Step 1 - Cloning
Clone repository into the folder you desire.

#### Step 2 - Download variables file
Download variables file [here](https://drive.google.com/file/d/1Y2iiIUdy493SiHe3zIxX-uxS3h8sZX-8/view?usp=sharing)

#### Step 3 - Put variables file into desired location
Put downloaded variable file into:
```
cloned folder location > project_root/yolo/checkpoints/yolov4-416/variables/
```

#### Step 4 - Download yolov4
Download yolov4 from [here](https://drive.google.com/open?id=1cewMfusmPjYWbrnuJRuKhPMwRe_b9PaT)

#### Step 5 - Put yolov4 into desired location 
Put ```yolov4.weights``` file into:
```
cloned folder location > project_root/yolo/data/
```

### Installing Dependencies
Make sure following depencies are installed correctly
#### Step 6 - Dependencies
- openCV Python **(Contrib Version)** ```pip install opencv-python-contrib```
- tensorflow ```pip install tensorflow```
- easydict ```pip install easydict```
- scipy ```pip install scipy```
- numpy ```pip install numpy```
- lxml ```pip install lxml```
- tqdm ```pip install tqdm```
- absl-py ```pip install absl-py```
- matplotlib ```pip install matplotlib```
- pillow ```pip install pillow```

### Running
Run main.py by typing **after navigating into the directory where main is present. **
```
python main.py
```
