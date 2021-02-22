# Process-Light-Fields-Captured-with-Lytro-Camera-via-Light-Field-Toolbox-for-MATLAB
This repository contains the source code and materials for processing light fields captured with a Lytro Camera, the [Light Field Toolbox for MATLAB](https://dgd.vision/Tools/LFToolbox/) (*with [license](LFToolbox0.5/LICENSE.txt)*) is implemented in order to obtain the sub-aperture images, the angular matrix at some fixed spatial point or all spatial points.

Moreover, this repository only contains two captured light fields as examples, the full dataset is avalible at [asdasd](asdasd) [1].

***Authors: Juan Felipe Jaramillo Hernández, María Fernanda Hernández Baena***

Contents Table
=================

<!--ts-->
   * [Process Light Fields Captured with Lytro Camera via Light Field Toolbox for MATLAB](#Process-Light-Fields-Captured-with-Lytro-Camera-via-Light-Field-Toolbox-for-MATLAB)
   * [Contents Table](#Contents-Table)
   * [Calibration](#Calibration)
   * [Extraction](#Extraction)
   * [Downsampling](#Downsampling)
   * [Video Maker](#Video-Maker)
   * [References](#References)
<!--te-->


### Calibration
In order to obtain the calibration data from you camera, it is required some previous steps:

The first one, is to locate the calibration files from you Lytro camera, this files are called *data.C.0, data.C.1, data.C.2, data.C.3* and usually, are located at *AppData/Local/Lytro/cameras*. Since each file is around 300 MB, these files are not contained in this repository. You'll extract white image calibration data from those. Once you found these files, place them at [Camera's folder](Cameras/sn-A102430881/). Then, you'll able to extract the white image calibration data.

The second step is to obtain the camera's matrix and dirtotion parameters, in order to rectify captured light fields. For this, you have to capture some calibration light fields of some checkerboard, the more corners and smallest squares, the better results. This repository contains 9 [calibration light fields](Cameras/sn-A102430881/CalSamples) captured on a checkerboard with 19x22 cornes with 4mm square size. If you want to use your own calibration samples, then remember to save them at Cameras/sn-A102430881/CalSamples.

Once your camera calibration data and your calibration light fields are on place, you'll just need to run [calibration.m](calibration) to adquire the calibration data: [CallInfo.json](Cameras/sn-A102430881/CalSamples/CalInfo.json), [CalibrationDatabase.mat](Cameras/CalibrationDatabase.mat)  for rectify purposes and [WhiteImageDatabase.mat](Cameras/WhiteImageDatabase.mat) for decoding and color correction on the light fields. This repository contains both rectify and decoding calibration data, so feel free to use them as well.


**Calibration Light Field Thumb and Rectified Thumb**

![Calibration](Cameras/sn-A102430881/CalSamples/raw2__Decoded_Thumb.png)
![Calibration Rectified](Cameras/sn-A102430881/CalSamples/raw2_rectified_Decoded_Thumb.png)

### Extraction

### Downsampling

### Video Maker

### References
[1] Light Field Toolbox for Matlab, available at https://dgd.vision/Tools/LFToolbox/
