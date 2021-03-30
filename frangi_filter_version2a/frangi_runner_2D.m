function [J, Scale, Direction] = frangi_runner_2D(filename)
subplot(1,2,1)
img2dGrayNamePath = fullfile('~', filename);
I = double(imread(filename));
size(I)
imagesc(I);
axis image

subplot(1,2,2);
colormap(gray);
[J,Scale,Direction] = FrangiFilter2D(I);
imagesc(J);
axis image
