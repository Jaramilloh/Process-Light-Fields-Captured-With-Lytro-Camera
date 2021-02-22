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

The second step is to obtain the camera's matrix and dirtotion parameters, in order to rectify captured light fields. For this, you have to capture some calibration light fields of some checkerboard, more the corners in it with less size, the better results. This repository contains 9 [calibration light fields](Cameras/sn-A102430881/CalSamples) captured on a checkerboard with 19x22 cornes with 4mm size. If you want to use your own calibration samples, then remember to save them at Cameras/sn-A102430881/CalSamples.

Once your camera calibration data and your calibration light fields are on place, you'll need to run [calibration.m](calibration) 




In order to obtain the Calibration data from you camera, as the calibration white images, camera's matrix parameters and dirtotion paremeters, you need to capture some light fields of a checkerboard. In this repository, you'll find 9 light fields captured (Cameras/sn-A102430881/CalSamples)


**Imagen de salida LR en RGB o escala de grises**

![Lenna - Imagen de salida LR rgb](Validacion/Imagenes_LR/lenna_bgr_sub-muestreada.png)
![Lenna - Imagen de salida LR gris](Validacion/Imagenes_LR/lenna_gray_sub-muestreada.png)

### Extraction

### Downsampling

### Video Maker

### References
[1] Light Field Toolbox for Matlab, available at https://dgd.vision/Tools/LFToolbox/
