# Human-Motion-Reconstruction
 
This project combines EasyMocap's Github project and Python's Django software to develope a user interface that automated the process of multi-video syncrhonization, intrinsic and extrinsic camera calibration, and human motion capture and reconstruction.

## Process

### Input video:
You can watch the demo video [here](https://drive.google.com/file/d/1BlU6zdOJ7lNy20Ruh_X7Za1-ZKFPQ0yO/view?usp=share_link).

### YOLO is used for human detection and HRNet is used for 2D keypoint detection:
<img width="963" alt="image" src="https://github.com/user-attachments/assets/b1a9cd3d-a0a5-434b-8d84-65b3c642bc3a">

### Multi-View Triangulation is used to estimate accurate 3D keypoints:
<img width="596" alt="image" src="https://github.com/user-attachments/assets/a1a8de37-5375-44c6-a177-cdc9de37e235">

### The SMPL model is fit to the 3D keypoints to obtain an occurate mesh:
