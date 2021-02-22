% Algorithm to process the light fields captured by a plenoptic camera
% Lytro first generation, in order to obtain the
% subaperture images through processing as correction of
% color, image rectification and light field decoding,
% Functions provided by the Light Field Toolbox for Matlab 
% https://dgd.vision/Tools/LFToolbox/

% Made by Juan Felipe Jaramillo Hernandez -
% j_jaramillo@javeriana.edu.co
% 09/02/2021


% Adding paths for LF Toolbox v0.5.1
fprintf('\nSelect path of Light Field Toolbox: ');
LFtbfolder = uigetdir( );
aux = append( LFtbfolder, '/LFMatlabPathSetup.m');
run( aux );

% Add the camera's calibration parameters to the calibration database
LFUtilProcessCalibrations ( 'Cameras' );

% A list is obtained with all the captured LFs
fprintf('\nSelect the folder containing LFs: ');
folder = uigetdir( );
fileList = dir( fullfile( folder, '*.lfp' ) );


% Angular Folder is created inside the folder containing LFs
aux = append( folder, '/Angular/' );
if ~exist(aux, 'dir')
    mkdir(aux);
end

% The file with the calibration parameters obtained from the
% calibration process is loaded
fprintf('\nSelect the CalInfo.json file (Usually Cameras/sn-A102430881/CalSamples/CalInfo.json): ');
[calfile, calpath] = uigetfile( );
aux = append( calpath, calfile );
LFMetadata = jsondecode( fileread( aux ) );

% Loop to process each LF individually 
for j = 1:( length( fileList ) )
       
        pth = append( folder, '/', fileList(j).name );
        fprintf('\nAnalizando LF: %s ', pth );
        tic

            % Captured LF is decoded 
            LFUtilDecodeLytroFolder( pth );

            % Color correction is performed applying the RGB information 
            % and correction Gamma found in LF metadata
            DecodeOptions.OptionalTasks = 'ColourCorrect';
            LFUtilDecodeLytroFolder( pth, [], DecodeOptions );

            % The decoded LF is loaded to obtain parameters of calibration
            LFname = append( folder, '/', fileList(j).name(1:8), '__Decoded.mat' );
            load( LFname, 'LF' );
            
            % The camera calibration parameters are modified to rectify the LF
            [LF, RectOptions] = LFCalRectifyLF( LF, LFMetadata );
            RectOptions.RectCamIntrinsicsH(1:2,1:2) = 0.25*RectOptions.RectCamIntrinsicsH(1:2,1:2);
            RectOptions.RectCamIntrinsicsH = LFRecenterIntrinsics( RectOptions.RectCamIntrinsicsH, size(LF) );
  
            % The LF is rectified
            DecodeOptions.OptionalTasks = 'Rectify';
            LFUtilDecodeLytroFolder( pth, [], DecodeOptions, RectOptions );
            
            % Decoded, rectified and color corrected LF is loaded again
            LFname = append( folder, '/', fileList(j).name(1:8), '__Decoded.mat' );
            load( LFname, 'LF' );
            
            % Contrast is adjusted according to the image histogram
            LF = LFHistEqualize( LF );

            % A folder to contain the angular portions images for each LF
            lffolder = append( folder, '/Angular/', fileList(j).name(1:8) );
            if ~exist(lffolder, 'dir')
                mkdir(lffolder);
            end
            % Loops to index spatial coordinates each 40 pixels:
            fprintf('\nExtracting angular sequence...' );
            cont = 1;
            for s = 2:20:376

                % Loop for vertical spatial coordinate
                for t = 2:20:376

                    % The name of the file to save is defined
                    cen = fix( cont/100 );
                    dec = fix( mod(cont,100)/10 );
                    und = mod( cont,10 );
                    aux = append( folder, '/Angular/',fileList(j).name(1:8),'/',fileList(j).name(1:8) );
                    auxx = append( '_',string(cen),string(dec),string(und),'.png' );
                    sbname = append(aux, auxx);

                    % Obtain a portion of 11x11 angular pixels at spatial position 's, t'
                    I = LFDisp( LF(2:10,2:10,t,s,:) );
                    F = I;        
                    % The subaperture image is saved
                    imwrite( F, sbname );
                    cont = cont + 1;
                end    
            end    

            % A folder to contain the downsampled angular portions images for each LF
            % each LF
            lffolder = append( folder, '/Angular/', fileList(j).name(1:8), '_downsampled' );
            if ~exist(lffolder, 'dir')
                mkdir(lffolder);
            end
            % Loop for horizontal spatial coordinate
            fprintf('\nExtracting angular sequence...' );
            cont = 1;
            for s = 2:20:376

                % Loop for vertical spatial coordinate
                for t = 2:20:376

                    % The name of the file to save is defined
                    cen = fix( cont/100 );
                    dec = fix( mod(cont,100)/10 );
                    und = mod( cont,10 );
                    aux = append( folder, '/Angular/',fileList(j).name(1:8),'_downsampled/',fileList(j).name(1:8) );
                    auxx = append( '_',string(cen),string(dec),string(und),'.png' );
                    sbname = append(aux, auxx);

                    % Obtain a portion of 5x5 angular pixels at spatial position 's, t'
                    I = LFDisp( LF(4:8,4:8,t,s,:) );
                    F = I;
                    % The subaperture image is saved
                    imwrite( F, sbname );
                    cont = cont + 1;
                end    
            end    
            
            % Se actualiza la previsualizacion del LF
            Thumb = LFDisp( LF );
            Thumbpth = append( folder, '/', fileList(j).name(1:8), '__Decoded_Thumb.png' );
            imwrite( Thumb, Thumbpth );
    
    toc
    delete( LFname );
    
end





