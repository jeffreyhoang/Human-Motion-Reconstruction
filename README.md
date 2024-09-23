# Human-Motion-Reconstruction
 
Combined EasyMocap's Github project and Python's Django software to develope a user interface that automated the process of multi-video syncrhonization, intrinsic and extrinsic camera calibration, and human motion capture and reconstruction.

## Process

### Input video:

### YOLO is used for human detection and HRNet is used for 2D keypoint detection:

### Multi-View Triangulation is used to estimate accurate 3D keypoints:

### The SMPL model is fit to the 3D keypoints to obtain an occurate mesh:
