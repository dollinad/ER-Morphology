function [J,Scale,Vx,Vy,Vz] = frangi_runner_3D(filename)

numImgs = 77;
vol = [];

% Loop over all the images in the folder.
for a=1:numImgs
    % Read the image.
    img2D = double(imread(filename,a));
    
    % This is a 2D scalar image. Store it in the volume.
    vol(:,:,a) = img2D;
end

figure(1);

% slice(vol, round(size(vol,2)/2), round(size(vol,1)/2), round(size(vol,3)/2));
% axis image; colormap gray;
% shading flat;   

figure(2);

[J,Scale,Vx,Vy,Vz] = FrangiFilter3D(vol);

slice(J, round(size(J,2)/2), round(size(J,1)/2), round(size(J,3)/2));
axis image; colormap gray;
shading flat;