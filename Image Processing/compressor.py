from PIL import Image, ImageSequence, TiffImagePlugin
import PIL
import os
import glob

# Compresses .tif files
# Not using this -- see cropping.py
def compress_images(directory=False):
    if directory:
        os.chdir(directory)

    pages = []

    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tif"):
                print(os.path.join(subdir, file))
                img = Image.open(os.path.join(subdir, file))

                for page in ImageSequence.Iterator(img):
                    new_size = (page.size[0]/4, page.size[1]/4)
                    page = page.resize(new_size)
                    pages.append(page)

                print ('Writing multipage TIF')
                with TiffImagePlugin.AppendingTiffWriter(os.path.join(subdir, "compressed_" + file)) as tf:
                    for page in pages:
                        page.save(tf)
                        tf.newFrame()

compress_images(os.path.dirname(os.path.abspath(__file__)))

# for f in *.tif; do out="$f.lzw.tif"; if tiffcp -c lzw "$f" "$out"; then touch -r "$f" "$out" && mv "$out" "$f"; else echo "ERROR with $f"; fi; done
