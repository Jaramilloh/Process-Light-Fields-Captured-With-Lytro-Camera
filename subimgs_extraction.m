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

% Tiled subaperture images Folder is created inside the folder containing LFs
aux = append( folder, '/Mosaicos/' );
if ~exist(aux, 'dir')
    mkdir(aux);
end

% Subaperture images Folder is created inside the folder containing LFs
aux = append( folder, '/Frames/' );
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

            % Subaperture images are extracted into a stuv matrix 
            fprintf('Extracting mosaic image...' );
            subaperture = LFDispTiles( LF(:,:, 2:end-2, 2:end-2, :) );
            %subaperture = LFDispTiles( LF(:,:,:,:,:) );
            I = LFDisp( subaperture );

            % Tiled subaperture images are saved
            fname = append( folder, '/Mosaicos/', fileList(j).name(1:8), '_stuv.png' );
            imwrite( I, fname );

            % A folder containing the subaperture images is created for
            % each LF
            lffolder = append( folder, '/Frames/', fileList(j).name(1:8) );
            if ~exist(lffolder, 'dir')
                mkdir(lffolder);
            end

            % Loops to index each subaperture image:
            % Loop for horizontal angular coordinate
            fprintf('\nExtracting image sequence...' );
            cont = 1;
            for s = 1:9

                % Starting conditions for the vertical angular coordinate
                if mod((s+1),2) == 0
                    init = 1;
                    finish = 9;
                    step = 1;
                else
                    init = 9;
                    finish = 1;
                    step = -1;
                end

                % Loop for vertical angular coordinate
                for t = init:step:finish

                    % The name of the file to save is defined
                    dec = fix( cont/10 );
                    und = mod( cont,10 );
                    aux = append( folder, '/Frames/',fileList(j).name(1:8),'/',fileList(j).name(1:8) );
                    auxx = append( '_',string(dec),string(und),'_', string(s),'_',string(t),'.png' );
                    sbname = append(aux, auxx);

                    % Obtain a subimage at angular position 's, t'
                    I = LFDisp( LF((t+1),(s+1),:,:,:) );

                    % Remove borders -> obtain spatial image of 376 x 376
                    [rows, cols, ch] = size( I );
                    
                    if (mod(rows, 2) ~= 0) && (mod(cols, 2) ~= 0)
                        F = I( 2:end-2,2:end-2,:);
                    elseif (mod(rows, 2) == 0) && (mod(cols, 2) ~= 0)
                        F = I( 2:end-1,2:end-2,:);
                    elseif (mod(rows, 2) ~= 0) && (mod(cols, 2) == 0)
                        F = I( 2:end-2,2:end-1,:);
                    end
                    
                    %F = I( 2:end-2,2:end-2,:);
                    %F = I;
                    
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





