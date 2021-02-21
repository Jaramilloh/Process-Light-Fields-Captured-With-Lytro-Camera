% Algorithm to spatially subsample the subaperture images
% obtained from light fields captured with a plenoptic Lytro camera
% first generation. A filter is implemented in frequency before sub-sampling
% the images in order to avoid aliasing effects.

% Made by Juan Felipe Jaramillo Hernandez -
% j_jaramillo@javeriana.edu.co
% 09/02/2021

% A list is obtained with all the container directories of the frames
fprintf('\nSelect the frames folder (usually at /Main/LF/Frames/) ');
folder = uigetdir( 'LF' );
folderList = dir( fullfile( folder, 'IMG*.*' ) );

% Loop to cycle through each directory
for i = 1:( length( folderList ) )
    
    % A list is obtained with the names of the frames within each directory
    fname = append( folder, '/', folderList(i).name );
    fileList = dir( fullfile( fname, '*.png' ) );
    fprintf('\n\nAt folder %s :', fname );
    
    % A directory containing the subsampled frames is created
    fdname = append( fname, '_downsampled' );
    if ~exist(fdname, 'dir')
        mkdir(fdname);
    end
    
    fprintf('\nSubsampling Images...');
    
    % Loop for each frame
    for j = 1:( length( fileList ))
        
        imgf = append( fname, '/', fileList(j).name );
        I = imread( imgf );
        
        % Image dimensions
        [n,n1,n2] = size( I );

        % The cutoff frequency is calculated to filter the image,
        % considering Nyquist's Theorem. A Gaussian Filter is implemented
        K = 4;
        sigmaf = (1/(2*K))*n; % Sigma in frequency
        sigma = n/(sigmaf*2*pi); % Sigma in space
        
        % The image is filtered in the frequency domain at the
        % specific cutoff frequency
        J = imgaussfilt( I, sigma, 'FilterSize', n+1, 'FilterDomain', 'frequency' );
        
        % The image is subsampled by a factor K
        Jdown = J(1:K:end,1:K:end,:);
        
        % The subsampled image is saved
        imgdf = append( fdname, '\dwn_', fileList(j).name);
        imwrite( Jdown, imgdf );
       
    end
    fprintf(' Done');
    
end



