% Algorithm to obtain the calibration parameters (parameters
% intrinsic and distortion of the lens and microlenses) of the plenoptic
% camera Lytro first generation, using 9 captures of a
% chess board with 22x19 corners and 4mm anchor. Functions provided by
% the Light Field Toolbox for Matlab https://dgd.vision/Tools/LFToolbox/

% Made by Juan Felipe Jaramillo Hernandez
% j_jaramillo@javeriana.edu.co
% 09/02/2021

% NOTE: this algorithm should only be executed as long as there is no
% of the CalInfo.json and WhiteImageDatabase.mat files 

% Adding paths for LF Toolbox v0.5.1
fprintf('\nSelect path of Light Field Toolbox: ');
LFtbfolder = uigetdir( );
aux = append( LFtbfolder, '\LFMatlabPathSetup.m');
run( aux );

% Extract calibration information from camera files
LFUtilUnpackLytroArchive( 'Cameras', 'data.C.0')

% Build a whiteimage database based on camera files extracted
LFUtilProcessWhiteImages( 'Cameras' );


% CALIBRATION - OBTAIN INTRINSIC AND DISTORTION CAMERA PARAMETERS 

% The LFs of checkerboard are decoded
LFUtilDecodeLytroFolder( 'Cameras/sn-A102430881/CalSamples/');
% Characteristics of the calibration board are defined
CalOptions.ExpectedCheckerSize = [22, 19];
CalOptions.ExpectedCheckerSpacing_m = 1e-3*[4.1, 4.0];
% The intrinsic and extrinsic parameters are obtained, the file in interest
% is called CalInfo.json, saved in CalSamples folder
LFUtilCalLensletCam( 'Cameras/sn-A102430881/CalSamples', CalOptions);
% Build a calibration databes based on the parameters obtained
LFUtilProcessCalibrations ( 'Cameras' );
