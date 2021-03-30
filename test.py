import matlab.engine
import os
eng = matlab.engine.start_matlab()


# pre requisites (notes from Cam):
# - download the matlab frangi filter - https://www.mathworks.com/matlabcentral/fileexchange/24409-hessian-based-frangi-vesselness-filter
#   - may need to install image processing add-on
# - frangi_runner.m must be in same foler as frangi-filter
#   - test frangi_runner.m in matlab to make sure not add-ons are needed
# - install matlab engine - https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html
# - i am running this in python 2.7 as that is the only version of python i have installed that is compatible w matlab engine, lmk if we should run in a more up to date version
# - will likely need ot update file paths below, not sure the easiest way around this


filepath = os.path.dirname(os.path.abspath(__file__))
# path to folder with frangi_runner
eng.addpath(r'/Users/cam/Documents/University/Third-Year/Spring/cmpt340/Project.nosync/frangi_filter_version2a',nargout=0)

# --- 2D IMAGE ---
user_input = raw_input("Run 2D? (y/n): ").lower()
if(user_input == 'y'):
    print("--- Running 2D Frangi Filter ---")
    # path to image folder
    image_filepath = os.path.join(filepath, "tiffs STED/g241 siCTRL/Image 1")
    print(image_filepath)

    # get all images
    tiff_files = []
    for tiff_file in os.listdir(image_filepath):
        tiff_files.append(tiff_file)

    # run for each image
    for file in tiff_files:
        image = os.path.join(image_filepath, file);
        j, scale, direction = eng.frangi_runner_2D(image, nargout=3)
        user_input = raw_input("Continue? (y/n): ").lower()
        if(user_input == 'n'): break

