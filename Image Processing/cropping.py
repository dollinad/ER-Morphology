from PIL import Image, ImageSequence, TiffImagePlugin
import PIL
import os
import glob

# Crops image from the center
def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def compress_images(directory=False):
    if directory:
        os.chdir(directory)

    pages = []

    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tif"):
                print(os.path.join(subdir, file))
                img = Image.open(os.path.join(subdir, file))

                # Crop all pages
                for page in ImageSequence.Iterator(img):
                    # Preferred cropping resolution: 475x475
                    page = crop_center(page, 475, 475)
                    pages.append(page)

                print ('Writing multipage TIF')
                with TiffImagePlugin.AppendingTiffWriter(os.path.join(subdir, "cropped_" + file)) as tf:
                    for page in pages:
                        page.save(tf)
                        tf.newFrame()

compress_images(os.path.dirname(os.path.abspath(__file__)))
