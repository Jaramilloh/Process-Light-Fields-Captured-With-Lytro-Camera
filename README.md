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

The second step is to obtain the camera's matrix and distortion parameters in order to successfully rectify the captured light fields. For this, you have to capture some calibration light fields of some checkerboard, the more corners and smallest squares, the better results. This repository contains 9 [calibration light fields](Cameras/sn-A102430881/CalSamples) captured on a checkerboard with 19x22 cornes and 4mm square size. Save calibration light fields at Cameras/sn-A102430881/CalSamples if you want to use your own samples.

Once your camera calibration data and your calibration light fields are on place, you'll just need to run [calibration.m](calibration) to adquire the calibration data. This program will automatically save the next files in their corresponding paths: [CallInfo.json](Cameras/sn-A102430881/CalSamples/CalInfo.json), [CalibrationDatabase.mat](Cameras/CalibrationDatabase.mat) for rectify purposes and [WhiteImageDatabase.mat](Cameras/WhiteImageDatabase.mat) for decoding and color correction on the light fields. Before extracting the previous files, you have to specify via GUI the [Light Field Toolbox path](LFToolbox0.5). This repository contains both rectify and decoding calibration data already extracted, so feel free to use them as well.

**Calibration Light Field Thumb and Rectified Thumb**

![Calibration](Cameras/sn-A102430881/CalSamples/raw2__Decoded_Thumb.png)
![Calibration Rectified](Cameras/sn-A102430881/CalSamples/raw2_rectified_Decoded_Thumb.png)

### Extraction

### Downsampling

### Video Maker

### References
[1] Light Field Toolbox for Matlab, available at https://dgd.vision/Tools/LFToolbox/
