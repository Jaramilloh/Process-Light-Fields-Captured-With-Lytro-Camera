# Process-Light-Fields-Captured-with-Lytro-Camera
This repository contains the source code and materials for processing light fields captured with a First Generation Lytro Camera, the [Light Field Toolbox for MATLAB](https://dgd.vision/Tools/LFToolbox/) (*with [license](LFToolbox0.5/LICENSE.txt) [1]*) is implemented in order to [decode, color correct and rectify](calibration.m) each light field in preparation to [obtain the sub-aperture images](subimgs_extraction.m). Also, an [angular light field downsampling](procesamiento_LF.py) code is implemented in order to create a dataset to train a deep neural network.

Moreover, this repository only contains two captured light fields as examples, the full dataset is avalible at [asdasd](asdasd) [2].

***Authors: Juan Felipe Jaramillo Hernández, María Fernanda Hernández Baena***

Table of Contents
=================

<!--ts-->
   * [Process Light Fields Captured with Lytro Camera](#Process-Light-Fields-Captured-with-Lytro-Camera)
   * [Table of Contents](#Table-of-Contents)
   * [Light Field Toolbox For MATLAB](#Light-Field-Toolbox-For-MATLAB)
   * [Calibration Data](#Calibration-Data)
   * [Sub-aperture Images Extraction](#Sub-aperture-Images-Extraction)
   * [Angular Downsampling](#Angular-Downsampling)
   * [References](#References)
      * 
<!--te-->

## Light Field Toolbox For MATLAB
The material in this repository wouldn't be possible without the [Light Field Toolbox for MATLAB](https://dgd.vision/Tools/LFToolbox/) [1], who may concern, our deepest thanks for making possible and available this processing pipeline for light fields.

First of all, you need to donwload the zipped [Light Field Toolbox for MATLAB](https://dgd.vision/Tools/LFToolbox/) [1]. Once donwloaded, please unzip the content in its corresponding [path](LFToolbox0.5) in order to use the algorithims implemented in this repository.

## Calibration Data
In order to obtain the calibration data from you camera, it is required some previous steps:

* First, you have to locate the calibration files from you Lytro camera, this files are called *data.C.0, data.C.1, data.C.2, data.C.3* and are usually located at *AppData/Local/Lytro/cameras*. Since each file is around 300 MB, these files are not contained in this repository. You'll extract white image calibration data from those. Once you found these files, place them inside this location: [Cameras/sn-A102430881/](Cameras/sn-A102430881/).

* Second, you have to capture some calibration light fields of some checkerboard, the more corners and smallest squares, the better results. This repository contains 9 [calibration light fields](Cameras/sn-A102430881/CalSamples) captured on a checkerboard with 19x22 cornes and 4mm square size. If you want to use your own samples, save them inside of [Cameras/sn-A102430881/CalSamples](Cameras/sn-A102430881/CalSamples).

Once your camera calibration data and your calibration light fields are on place, you'll just need to run [calibration.m](calibration.m) to adquire the calibration data; camera matrix and distortion parameters, white image calibration grids and others. Before processing the previous files, you have to specify via GUI the Light Field Toolbox path, beign [LFToolbox0.5/](LFToolbox0.5/) in this repository.

The program will automatically save the next files in their corresponding paths: CallInfo.json (at [Cameras/sn-A102430881/CalSamples/](Cameras/sn-A102430881/CalSamples/CallInfo.json)), CalibrationDatabase.mat (at [Cameras/](Cameras/CalibrationDatabase.mat)) for rectify purposes and WhiteImageDatabase.mat (at [Cameras/](Cameras/WhiteImageDatabase.mat)) for decoding and color correction purposes. This repository contains both [rectify](Cameras/sn-A102430881/CalSamples/CallInfo.json) and [decoding](Cameras/WhiteImageDatabase.mat) calibration data already extracted, so feel free to use them as well.

**Calibration Light Field Thumb**

![Calibration](Cameras/sn-A102430881/CalSamples/raw2__Decoded_Thumb.png)

**Calibration Light Field Rectified Thumb**

![Calibration Rectified](Cameras/sn-A102430881/CalSamples/raw2_rectified_Decoded_Thumb.png)

## Sub-aperture Images Extraction

Once calibration data is available, you can proceed to process your own captured light fields. Place these light fields at the LF folder [LF/](LF/). Then, you just have to run [subimgs_extraction.m](subimgs_extraction.m). This program will ask you first to select the Light Field Toolbox path ([LFToolbox0.5/](LFToolbox0.5) in this repository), then, it will ask you to select the LF folder path [LF/](LF/), and finally, it will ask you to select the [CallInfo.json file's path](Cameras/sn-A102430881/CalSamples/CalInfo.json).

Therefore, the program will decodify each .lfp file placed in the LF folder, correcting the color on it and rectifying the scene. Then, it will extract a mosaic image, which is composed by the sub-aperture images, therefore, saving these at [LF/Frames](LF/Frames). Note: This code actually crops the center of each sub-aperture image to 256x256 dimensions.

**Light Field Central View Thumb (Color corrected and rectified)**

![LF_thumb](LF/IMG_0001__Decoded_Thumb.png)

**Sub-aperture Images as Sequence of Images**

![video1](Resources/IMG_0001_video.gif)

### Angular Downsampling

[procesamiento_LF.py](procesamiento_LF.py) will angular downsample all the original sub-aperture images inside the directory [LF/Frames](LF/Frames), extracted from before, by extracting a pixel matrix that corresponds to the angular resolution at each spatial point. The program will save the results inside the same directory but creating new sub-folders, corresponding to the sub-aperture images angular downsampled (example: [LF/Frames/IMG_0001_adownsampled](LF/Frames/IMG_0001_adownsampled)). 

**Angular Downsampled Sub-aperture Images as Sequence of Images**

![video2](Resources/IMG_0001_adonwsampled.gif)

Also, it will synthesize the complete original light field structure arranged by its angular resolution at each spatial point and the spatial resolution at each angular point, and its equivalent but angular downsampled.

**Light Field Structure *stuv***

![LF1](LF/LF_stuv/IMG_0001/IMG_0001_stuv.png)

**Angular Downsampled Light Field Structure *stuv***

![LF2](LF/LF_stuv/IMG_0001_adownsampled/IMG_0001_adownsampled_stuv.png)

**Light Field Structure *uvst***

![LF3](LF/LF_uvst/IMG_0001/IMG_0001_uvst.png)

**Angular Downsampled Light Field Structure *uvst***

![LF4](LF/LF_uvst/IMG_0001_adownsampled/IMG_0001_adownsampled_uvst.png)

This code will generate a [.h5 dataset](https://drive.google.com/uc?id=1FkXZCNqhB57jSXJXwZC0nuWHVbpDKGPY) file with random selected HR and LR angular matrices for each light field in order to train a deep learning network to super resolve the angular resolution of a light field. Moreover, this code will interpolate the angular downsampled pixel matrix via nearest, bicubic and lanczos interpolation, synthesizing the corresponding new sub-aperture images, thus comparing our implemented super-resolution model with these results. Finally, this code will generate a .mp4 video for each LF represented as sub-aperture images.

## References

[1] Light Field Toolbox for Matlab, available at https://dgd.vision/Tools/LFToolbox/

[2] F. J. Hernandez, “Plants captured with lytro 1st gen  dataset,” May2021. [Online]. Available: https://osf.io/qrm2x/?viewonly=76068daaca72497fa6bce50bb3fc0ccb


To cite this work:
@misc{Jaramillo2021a,
title={{Process Light Fields Captured with Lytro Camera}},
url={https://github.com/Jaramilloh/Process-Light-Fields-Captured-With-Lytro-Camera},
publisher={GitHub},
author={Jaramillo, Felipe},
year={2021},
month={May}
}