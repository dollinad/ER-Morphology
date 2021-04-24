function Voxel_data = vesselness_function(Lambda1, Lambda2, Lambda3)

% Calculate absolute values of eigen values
LambdaAbs1=abs(Lambda1);
LambdaAbs2=abs(Lambda2);
LambdaAbs3=abs(Lambda3);

% The Vesselness Features
Ra=LambdaAbs2./LambdaAbs3;
Rb=LambdaAbs1./sqrt(LambdaAbs2.*LambdaAbs3);

% Second order structureness. S = sqrt(sum(L^2[i])) met i =< D
S = sqrt(LambdaAbs1.^2+LambdaAbs2.^2+LambdaAbs3.^2);
A = 2*0.5^2; B = 2*0.5^2;  C = 2*500^2;

% Free memory
clear LambdaAbs1 LambdaAbs2 LambdaAbs3

%Compute Vesselness function
expRa = (1-exp(-(Ra.^2./A)));
expRb =    exp(-(Rb.^2./B));
expS  = (1-exp(-S.^2./C));
keyboard
% Free memory
clear S A B C Ra Rb

%Compute Vesselness function
Voxel_data = expRa.* expRb.* expS;