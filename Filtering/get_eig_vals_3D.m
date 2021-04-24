function [Lambda1, Lambda2, Lambda3] = get_eig_vals_3D(filename, numImgs)

disp("--- Matlab Calculations --- ")
vol = [];

% Loop over all the images in the folder.
disp("Assembling Volume"); 
for a=1:numImgs
    % Read the image.
    img2D = double(imread(filename,a));
    
    % This is a 2D scalar image. Store it in the volume.
    vol(:,:,a) = img2D;
end

disp("Calculating Hessian Matrix");
[Dxx, Dyy, Dzz, Dxy, Dxz, Dyz] = Hessian3D(vol, 1);
disp("Calculating Eigenvalues");
[Lambda1,Lambda2,Lambda3,Vx,Vy,Vz]=eig3volume(Dxx,Dxy,Dxz,Dyy,Dyz,Dzz);
disp("--- Exiting Matlab  --- ")